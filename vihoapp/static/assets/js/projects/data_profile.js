// when u click run button and call rest apis to run profiling module.
function runProfile(id, token) {
    $.ajax({
        type:"POST",
        url:"/apis/v1/profile/",
        data:{
            id :id,
            'csrfmiddlewaretoken': token
        },
        dataType   : "json",
        success: function(data) {
            if(data.task_id != null) {
                let data1 = localStorage.getItem("data_profile_ids");
                if(data1 == null) {
                    localStorage.setItem("data_profile_ids", JSON.stringify([{
                        task_id: data.task_id,
                        profile_id:id,
                    }]))
                }
                else {
                    data1 = JSON.parse(data1);
                    data1.push({
                        task_id: data.task_id,
                        profile_id:id,
                    });
                    localStorage.setItem("data_profile_ids", JSON.stringify(data1));
                }
                get_data_profile_status();
            }
        }
    })
}


// Define NonPrintable Data and punctuation table
let graphObject = null;
var NonPrintableData = {
    labels: ["Leading", "Trailing", "Non-Printable"],
    datasets: [{
        label: "Count",
        backgroundColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(255, 205, 86, 1)',
              'rgba(75, 192, 192, 1)',

            ],
        }
    ]
};
var punctuationTable = $("#punctuation-table").DataTable({
    scrollY: "40vh",
    scrollCollapse: true,
    paging: false,
    searching:false,
  });


//Display Non-Printable Character Graph
function displayNonPrintable(profile_id, column_index) {
    $("#chartModalTitle").html("Non-Printable Statistics");
    if(graphObject) graphObject.destroy();
    $.ajax({
        type: "GET",
        url: "/data-profile/profile/result/nonPrintableDetail?profile_id=" + profile_id + "&profile_column=" + column_index,
        dataType: "json",
        success: function (data) {
            NonPrintableData.datasets[0].data = data.data;

            const canvasCTX = document.getElementById("graphCanvas").getContext("2d");
            graphObject = new Chart(canvasCTX, {
                type:'bar',
                data: NonPrintableData,
                options:{
                    plugins:{
                        legend:{
                            display:false,
                        }
                    }
                }
            });
        }
    });

    $("#chartModal").modal("show");
}


//Display Non-Printable Character Graph
var NullFilledData = {
    labels: ["Filled", "Null"],
    datasets: [{
        label:"Count:",
        backgroundColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
        ],
        hoverOffset: 4
    }]
};
function displayNullFilled(profile_id, column_index) {
    $("#chartModalTitle").html("Null/Filled Statistics");
    if(graphObject) graphObject.destroy();
    $.ajax({
        type: "GET",
        url: "/data-profile/profile/result/nullFilled?profile_id=" + profile_id + "&profile_column=" + column_index,
        dataType: "json",
        success: function (data) {
            NullFilledData.datasets[0].data = data.data;

            const canvasCTX = document.getElementById("graphCanvas").getContext("2d");
            graphObject = new Chart(canvasCTX, {
                type:'doughnut',
                data:NullFilledData,
                options:{
                    aspectRatio:2
                }
            });
        }
    });

    $("#chartModal").modal("show");
}

// Display puncutation table
function displayPunctuation(profile_id, column_index) {
    $.ajax({
        type: "GET",
        url: "/data-profile/profile/result/punctuation?profile_id=" + profile_id + "&profile_column=" + column_index,
        dataType: "json",
        success: function (data) {
            punctuationTable.clear();
            for (key in data.data) {
                punctuationTable.row.add([
                        key,
                        data.data[key],
                        Math.round(data.data[key] / data.total_records * 100).toFixed(2) +"%",
                    ]).draw();
            }
        }
    });

    $("#tableModal").modal("show");
}

// Display Patterns
function displayPattern(profile_id, column_index) {
    if(graphObject) graphObject.destroy();
    $("#pattern-table tbody").html("");
    $.ajax({
        type: "GET",
        url: "/data-profile/profile/result/pattern?profile_id=" + profile_id + "&profile_column=" + column_index,
        dataType: "json",
        success: function (data) {
           console.log(data);
           var html = "";
           for(let i = 0; i < data.data.length; i ++) {
               html += "<a class='list-group-item list-group-item-action d-flex justify-content-between align-items-center' data-bs-toggle='list' " +
                   "href='#list-home' role='tab' aria-controls='list-home' onclick='displayGraphPattern(" + profile_id + "," + column_index + "," +
                   data.data[i].pattern.id + ")'>" +data.data[i].pattern.name + "<span class='badge badge-danger rounded-pill'>" + data.data[i].valid + "</span></a>";
           }
           $("#patternModal #list-tab").html(html);

        }
    });
    $("#patternModal").modal("show");

}
var patternData = {
    labels: ["Total", "Valid", "Invalid"],
    datasets: [{
        label: "Count",
        backgroundColor: [
              'rgba(255, 99, 132, 1)',
              'rgb(36, 105, 92)',
              'rgba(255, 205, 86, 1)',
            ],
        }
    ]
};
// Display pattern Graph
function displayGraphPattern(profile_id, column_index, pattern_id) {
    if(graphObject) graphObject.destroy();
    $("#pattern-table tbody").html("");
    $.ajax({
        type: "GET",
        url: "/data-profile/profile/result/pattern/detail?profile_id=" + profile_id + "&profile_column=" + column_index + "&pattern_id=" + pattern_id,
        dataType: "json",
        success: function (data) {
           patternData.datasets[0].data = data.graphData;
           const canvasCTX = document.getElementById("pattern-graph").getContext("2d");
           graphObject = new Chart(canvasCTX, {
                type:'bar',
                data: patternData,
                options:{
                     events:['click'],
                     onClick: (event, array) => {
                        if(array[0]) {
                            let html = "";
                            // when u click total bar
                            if (array[0].index == 0) {
                               for(let i = 0 ; i < data.DetectedData.length ; i ++) {
                                   if (data.DetectedData[i].valid == 1)
                                       html += "<tr><td class='bg-primary'>" + data.DetectedData[i].data + "</td></tr>";
                                   else
                                       html += "<tr><td class='bg-warning'>" + data.DetectedData[i].data + "</td></tr>";
                               }

                            }

                            // when u click valid bar
                            if (array[0].index == 1) {
                               for(let i = 0 ; i < data.DetectedData.length ; i ++) {
                                   if (data.DetectedData[i].valid == 1)
                                       html += "<tr><td class='bg-primary'>" + data.DetectedData[i].data + "</td></tr>";
                               }

                            }
                            // when u click invalid bar
                            if(array[0].index == 2) {
                                for(let i = 0 ; i < data.DetectedData.length ; i ++) {
                                   if (data.DetectedData[i].valid == 0)
                                       html += "<tr><td class='bg-warning'>" + data.DetectedData[i].data + "</td></tr>";
                               }
                            }
                            $("#pattern-table tbody").html(html);
                        }
                    },
                    plugins:{
                        legend:{
                            display:false,
                        }
                    }
                }
           });


           let html = "";

           for(let i = 0 ; i < data.DetectedData.length ; i ++) {
               if (data.DetectedData[i].valid == 1)
                   html += "<tr><td class='bg-primary'>" + data.DetectedData[i].data + "</td></tr>";
               else
                   html += "<tr><td class='bg-warning'>" + data.DetectedData[i].data + "</td></tr>";
           }
           $("#pattern-table tbody").html(html);


        }
    });
}

// Display the distinct table
function displayDistinct(profile_id, column_index) {
    var distinctTable = $("#distinct-table").DataTable({
        processing: true,
        serverSide: true,
        destroy:true,
        searching: false,
        scrollY: "40vh",
        scrollCollapse: true,
        ajax:{
            url:"/data-profile/profile/result/distinct?profile_id=" + profile_id + "&profile_column=" + column_index,
        },
        "columns": [
            { "data": "key" },
            { "data": "frequency" },
            {"data" : "percent"}

        ],
        "order":[[2, "desc"]]
      });



    $("#distinctModal").modal("show");
}

// Show all the detailed Records by clicking numbers
function accuracy_detail(profile_id, attr, column_index) {

    $("#accuracy_value_header").data("profile-id", profile_id)
    $("#accuracy_value_header").data("attr", attr)
    $("#accuracy_value_header").data("column_index-id", column_index)
    $("#accuracy-value-table").DataTable({
        processing: true,
        serverSide: true,
        destroy:true,
        searching: false,
        scrollY: "40vh",
        scrollCollapse: true,
        ajax:{
            url:"/data-profile/profile/result/detail?profile_id=" + profile_id + "&attr=" + attr + "&index=" + column_index,
        },
        "columns": [
            { "data": "name" },
        ],
      });

    $("#accuracy_value_modal").modal("show");
}

//export records to excel file
function exportRecords() {
    var profile_id = $("#accuracy_value_header").data("profile-id")
    var attr = $("#accuracy_value_header").data("attr")
    var column_index = $("#accuracy_value_header").data("column_index-id")
    $.ajax({
        type:"GET",
        url:"/data-profile/profile/result/detail/export",
        data:{
            profile_id :profile_id,
            attr:attr,
            index:column_index
        },
        xhrFields:{
            responseType: 'blob'
        },
        success: function(result) {
            var blob = result;
            var downloadUrl = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = downloadUrl;
            a.download = attr + ".xlsx";
            document.body.appendChild(a);
            a.click();
        }
    })
}

//Get ZIP Data from server
function getGeoData(profile_id, column_index) {
    $("#geo-value-table").DataTable({
        processing: true,
        serverSide: true,
        destroy:true,
        searching: false,
        scrollY: "40vh",
        scrollCollapse: true,
        ajax:{
            url:"/data-profile/profile/result/geo?profile_id=" + profile_id + "&index=" + column_index,
        },
        "columns": [
            { "data": "name" },
        ],
      });

    $("#geo-value-modal").modal("show");
}

// Get Geo Map HTML Response with selected postal code
function displayGEO(postal_code) {
    $.ajax({
        type:"GET",
        url:"/data-profile/profile/result/showGEO",
        data:{
            postal_code:postal_code
        },
        success: function(result) {
            $("#geo-display-body").html(result);

            $("#geo-value-modal").hide();
            $("#geo-display-modal").modal("show");
        }
    })

}

(function($) {

    //draw histogram of distinct table
    for(let i =0 ; i < $("#uniqueness table tbody").children().length; i ++) {
        let keyData = JSON.parse($("#uniqueness table tbody #histogram-key_" + i).val());
        let valueData = JSON.parse($("#uniqueness table tbody #histogram-value_" + i).val());
        let distinct_histogram_option = {
            series: [{
                name: 'frequency',
                data:valueData
            }],
            chart: {
                height:120,
                width:240,
                type: 'bar',
                toolbar: {
                  show: false
                },
            },
            plotOptions: {
             bar: {
              dataLabels: {
                position: 'top', // top, center, bottom
              },

             columnWidth: '30%',
             startingShape: 'rounded',
             endingShape: 'rounded',
             colors: {
                backgroundBarColors: ["#d8e3e5"],
                backgroundBarOpacity: 1,
                backgroundBarRadius: 9
              },
            }
            },
            dataLabels: {
                enabled: false,

                offsetY: -10,
                style: {
                    fontSize: '12px',
                    colors: ["#912efc"]
                }
            },

            xaxis: {
                position: 'bottom',
                categories:keyData,
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },

                labels:{
                    show:false
                }
            },
            yaxis: {
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false,
                },
                labels: {
                    show: false,
                    formatter: function (val) {
                      return val;
                    }
                }
            },
            colors: [vihoAdminConfig.secondary],
        };
        let histogramChart = new ApexCharts(document.querySelector("#uniqueness table tbody #histogram-bar_" + i),distinct_histogram_option);
        histogramChart.render();

        // catch close display geograph modal event
        $("#geo-display-modal").on("hidden.bs.modal", function () {
           $("#geo-value-modal").show()
        });
    }
})(jQuery);


