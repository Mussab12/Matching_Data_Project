import json

# Example JSON string
json_data = '''
{
    "id": 1,
    "data1": [
        {
            "id": 2,
            "ZIP": "076242613",
            "City": "Closter",
            "Email": "vjaggi@murphswine.com",
            "Phone": "7713951980",
            "State": "NJ",
            "Address": "106 Vervalen St",
            "Industry": "Wines-Retail",
            "Birthdate": "01-12-1981",
            "Modify Date": "22-12-2003",
            "National ID": "888413278",
            "Account Code": "99212613",
            "Company Name": "Murphy's Fine Wine",
            "Creation Date": "27-03-2001",
            "Demo Reference": "1. National ID Match 1",
            "Contact Last Name": "Yaggi",
            "Contact First Name": "Vick",
            "Contact Middle Initial": "David",
            "RelatedObject": 3
        },
        {
            "id": 3,
            "ZIP": "123456789",
            "City": "Sample City",
            "Email": "sample@email.com",
            "Phone": "1234567890",
            "State": "SS",
            "Address": "123 Main St",
            "Industry": "Sample Industry",
            "Birthdate": "01-01-2000",
            "Modify Date": "01-01-2000",
            "National ID": "123456789",
            "Account Code": "987654321",
            "Company Name": "Sample Company",
            "Creation Date": "01-01-2000",
            "Demo Reference": "2. Sample Reference",
            "Contact Last Name": "Doe",
            "Contact First Name": "John",
            "Contact Middle Initial": "M"
        }
    ]
}
'''

# Parse the JSON
data = json.loads(json_data)

# Map the relationships
mapping = {}
for obj in data["data1"]:
    mapping[obj["id"]] = obj.get("RelatedObject")

# Print the mapping
print(mapping)
