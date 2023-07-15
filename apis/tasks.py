import json
import logging
import re
from string import punctuation
import operator
import numpy as np
from celery import Celery
from leven import levenshtein
from sklearn.cluster import dbscan

from data_profile.models import DataProfile, DataPattern, DataProfileHistory
from vihoapp.global_func import checkifDataType, checkDateType, checkZipCode
from apis.tests import test_data
from apis.tests import profile_columns
import pandas as pd
from datetime import datetime

from vihoapp.models import User

app = Celery("viho")


@app.task(bind=True)
def data_profile_task(self, id, user_id):
    """
        Task for profiler
            :param
                @id - profile id
                @user - user who runs this task
    """

    start_time = datetime.now()
    profile = DataProfile.objects.get(pk=id)

    profile.status = "DOING"
    profile.save()

    self.update_state(state="PROGRESS", meta={"current": 0})

    total_rows = len(test_data)

    # define variables to store the results.
    maxlen_column = []
    character_column = []
    field_column = []
    type_column = []
    patternDetection_column = []
    precision_column = []
    geomap_column = []
    # Get selected RegEx List
    selectedRegExList = DataPattern.objects.filter(selected=True).values()

    column_index = 0
    column_length = len(profile_columns)

    # Define variables to calculate total score
    accuracy_null_score = 10
    accuracy_character_score = 10
    accuracy_outlier_score = 10
    accuracy_punctuation_score = 10
    accuracy_pattern_score = 10
    uniqueness_score = 30
    conformity_score = 20

    for column_item in profile_columns.keys():

        maxlen_item = -1
        contain_numbers = 0
        numbers_only = 0
        contain_letters = 0
        letters_only = 0
        contain_letters_numbers = 0
        punctuation_count = {}
        leading_space = 0
        trailing_space = 0
        non_printable_chracter = 0
        null_fields = 0
        outlier_detection = 0
        distinct_values = {}
        zip_count = 0
        patternDetection = []
        outlierData = []

        data_type_per_column = {
            "type": profile_columns[column_item],
            "valid": 0,
            "invalid": 0,
            "format": "",
        }
        date_type_column = {}
        valid_data_per_column = []
        precision_value = {
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "mode": None,
            "extreme": None
        }

        # Initialize the punctuation and pattern detection array
        for p in punctuation:
            punctuation_count[p] = 0
        for pattern in selectedRegExList:
            patternDetection.append(0)

        for item in test_data:
            column_data = item[column_item]

            # check if data is null or blank.
            if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
                null_fields += 1
                continue

            # check if this data is zip code
            if checkZipCode(column_data):
                zip_count += 1

            # check the Date Type to classify valid and invalid data
            if checkifDataType(profile_columns[column_item], column_data):
                data_type_per_column["valid"] += 1
                valid_data_per_column.append(column_data)
            else:
                data_type_per_column["invalid"] += 1

            # check if the data type is date and if date, determine the date format
            if profile_columns[column_item] == "string" or profile_columns[column_item] == "date":
                date_format = checkDateType(column_data)
                if date_format == "None":
                    valid_data_per_column.pop()
                if date_format in date_type_column.keys():
                    date_type_column[date_format] += 1
                else:
                    date_type_column[date_format] = 1

            # Store data to calculate outlier
            outlierData.append(column_data)

            # Calculate maxlen of data
            if len(column_data) > maxlen_item:
                maxlen_item = len(column_data)

            # Calculate distinct values
            if column_data in distinct_values.keys():
                distinct_values[column_data] += 1
            else:
                distinct_values[column_data] = 1

            # set pattern Detection
            for index, pattern in enumerate(selectedRegExList):
                try:
                    patternRegEx = re.compile(pattern["pattern"])
                    if patternRegEx.match(column_data):
                        patternDetection[index] += 1
                except Exception as e:
                    logging.getLogger().debug("Pattern is invalid.")
            # Calculate accuracy tab attributes
            digit_contain = any(c.isdigit() for c in column_data)
            letter_contain = any(not c.isdigit() for c in column_data)
            contain_numbers += digit_contain
            contain_letters += letter_contain
            numbers_only += column_data.isnumeric()
            letters_only += not digit_contain
            contain_letters_numbers += (digit_contain and letter_contain) and not (
                        column_data.isnumeric() or not digit_contain)

            for p in punctuation:
                if p in column_data:
                    punctuation_count[p] += 1
            leading_space += column_data.startswith(' ')
            trailing_space += column_data.endswith(' ')
            non_printable_chracter += not column_data.isprintable()

        # Define levishetein func to calculate distance between two strings
        def lev_metric(x, y):
            i, j = int(x[0]), int(y[0])  # extract indices
            return levenshtein(outlierData[i], outlierData[j])

        X = np.arange(len(outlierData)).reshape(-1, 1)
        core_samples, labels = dbscan(X, metric=lev_metric, eps=5, min_samples=2)
        for label in labels:
            if label == -1:
                outlier_detection += 1

        # Remove punctuation count if 0
        for p in punctuation:
            if punctuation_count[p] == 0:
                punctuation_count.pop(p)

        # check if the type is date and set format
        max_date_key = max(date_type_column.items(), key=operator.itemgetter(1))[0]
        if max_date_key != "None":
            data_type_per_column["type"] = "date"
            data_type_per_column["valid"] = date_type_column[max_date_key]
            data_type_per_column["format"] = max_date_key
            data_type_per_column["invalid"] = len(test_data) - null_fields - date_type_column[max_date_key]

        # calculate the precision value
        if data_type_per_column["type"] == "date":
            df = pd.DataFrame(dict(data=valid_data_per_column))
            df.data = pd.to_datetime(df.data)
            precision_value["min"] = datetime.strftime(pd.to_datetime(df.min().data).to_pydatetime(),
                                                       data_type_per_column["format"])
            precision_value["max"] = datetime.strftime(pd.to_datetime(df.max().data).to_pydatetime(),
                                                       data_type_per_column["format"])
            precision_value["mean"] = datetime.strftime(pd.to_datetime(df.mean().data).to_pydatetime(),
                                                        data_type_per_column["format"])
            precision_value["median"] = datetime.strftime(pd.to_datetime(df.median().data).to_pydatetime(),
                                                          data_type_per_column["format"])
            precision_value["mode"] = datetime.strftime(pd.to_datetime(df.mode().data[0]).to_pydatetime(),
                                                        data_type_per_column["format"])
            df["extreme"] = df.data - df.median().data
            extreme_index = df.extreme.idxmax()
            precision_value["extreme"] = datetime.strftime(pd.to_datetime(df.data[extreme_index]).to_pydatetime(),
                                                           data_type_per_column["format"])

        if data_type_per_column["type"] == "int" or data_type_per_column["type"] == "double":
            df = pd.DataFrame(dict(data=valid_data_per_column))
            df.data = pd.to_numeric(df.data)
            precision_value["min"] = df.min().data
            precision_value["max"] = df.max().data
            precision_value["mean"] = df.mean().data
            precision_value["median"] = df.median().data
            precision_value["mode"] = df.min().data
            df["extreme"] = df.data - df.median().data
            extreme_index = df.extreme.idxmax()
            precision_value["extreme"] = df.data[extreme_index]


        # check if column is zip code
        if zip_count >= (len(test_data) - null_fields) * 0.9:
            geomap_column.append(column_item)
        # store all calculated results
        precision_column.append(precision_value)
        type_column.append(data_type_per_column)
        patternDetection_column.append(patternDetection)
        maxlen_column.append(maxlen_item)
        character_column.append({
            "contain_numbers": contain_numbers,
            "contain_letters": contain_letters,
            "numbers_only": numbers_only,
            "letters_only": letters_only,
            "contain_letters_numbers": contain_letters_numbers,
            "punctuation_count": punctuation_count,
            "leading_space": leading_space,
            "trailing_space": trailing_space,
            "non_printable_character": non_printable_chracter,
        })
        field_column.append({
            "null_fields": null_fields,
            'filled_fields': len(test_data) - null_fields,
            "distinct_fields": len(distinct_values),
            "outlier_detection": outlier_detection,
        })

        # Calculate the overall score
        if null_fields >= total_rows * 0.4:
            accuracy_null_score = 0
        if (leading_space + trailing_space + non_printable_chracter) >= total_rows * 0.2:
            accuracy_character_score = 0
        if outlier_detection >= total_rows * 0.2:
            accuracy_outlier_score = 0
        if sum([punctuation_count[item] for item in punctuation_count]) >= total_rows * 0.2:
            accuracy_punctuation_score = 0
        if len(patternDetection) == 0 or max(patternDetection) < total_rows * 0.7:
            accuracy_pattern_score = 0
        if len(distinct_values) >= total_rows * 0.4:
            uniqueness_score = 0
        if data_type_per_column["invalid"] >= total_rows * 0.1:
            conformity_score = 0
        self.update_state(state="PROGRESS", meta={"current": 5 + column_index / column_length * 90})
        column_index += 1

    # save result to db
    total_data = {
        "total_rows": total_rows,
        "score": {
            "accuracy": accuracy_null_score + accuracy_character_score + accuracy_pattern_score + accuracy_punctuation_score + accuracy_outlier_score,
            "uniqueness": uniqueness_score,
            "conformity": conformity_score,
        },
        "maxlen_columns": maxlen_column,
        "character_columns": character_column,
        "pattern_columns": patternDetection_column,
        "field_column": field_column,
        "type_column": type_column,
        "precision_column": precision_column,
        "selected_patterns": list(selectedRegExList.values()),
        "geomap_columns": geomap_column
    }

    self.update_state(state="PROGRESS", meta={"current": 95})
    result = json.dumps(total_data)
    profile.status = "DONE"

    # Save this result to profile history
    user = User.objects.get(pk=user_id)
    profile_history = DataProfileHistory(profile_id=id, profile_user=user, profile_result=result,
                                         profile_time=(datetime.now() - start_time).seconds)
    profile_history.save()

    # End time
    profile.save()
    return True
