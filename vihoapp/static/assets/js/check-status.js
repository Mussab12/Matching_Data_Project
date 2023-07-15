$(function() {
    get_data_profile_status();
});

//Check the profiling running status and updates the status every seconds.
function get_data_profile_status() {
    // get task ids from localstorage
    let idData = localStorage.getItem("data_profile_ids");
    if(idData != null) {
        // call profile status api
        $.ajax({
        type:"POST",
        url: "/apis/v1/profile/status/",
        data:{
            'task_ids': idData,
        },
        success: function(data) {

            data = data.result;
            let newData = JSON.parse(idData);
            for(let i = 0; i < data.length; i++) {
                const index = newData.findIndex(item => item.task_id == data[i].task_id);
                if( index != -1) {

                    // if status is failure then remove data and set status as pending
                    if (data[i].state == "FAILURE") {{
                        $("#data-profile-" + newData[index].profile_id + " #status").html("PENDING");
                        $("#data-profile-" + newData[index].profile_id + " #status").attr("class", "badge badge-warning");
                        newData.splice(index, 1);
                    }}
                    // if status is success then remove index and set status as DONE
                    if(data[i].state == "SUCCESS") {
                        $("#data-profile-" + newData[index].profile_id + " #status").html("DONE");
                        $("#data-profile-" + newData[index].profile_id + " #status").attr("class", "badge badge-primary");
                        $("#data-profile-" + newData[index].profile_id + " #display-percent").html("100%");
                        $("#data-profile-" + newData[index].profile_id + " #display-bar").css("width", "100%");
                        newData.splice(index, 1);

                    }
                    // if status is progress then set status as DOING and display progress
                    if(data[i].state == "PROGRESS") {
                        //get % of current working thread
                        const donePercent = data[i].progress.current.toFixed(2);
                        $("#data-profile-" + newData[index].profile_id + " #status").html("DOING");
                        $("#data-profile-" + newData[index].profile_id + " #status").attr("class", "badge badge-danger");
                        $("#data-profile-" + newData[index].profile_id + " #display-percent").html(donePercent + "%");
                        $("#data-profile-" + newData[index].profile_id + " #display-bar").css("width", donePercent + "%");
                    }
                }
            }
            localStorage.setItem("data_profile_ids", JSON.stringify(newData));

            if(newData.length != 0) {
               setTimeout(function() {
                   get_data_profile_status()
               }, 1000);
            }
        }
    })
    }


}


