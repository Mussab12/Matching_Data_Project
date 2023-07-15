//Pattern table Initialization
let table = $("#pattern-table").DataTable({
    columnDefs: [{
        orderable: false,
        className: 'select-checkbox',
        targets:   0
    }],
    columns: [
        { data:"selected"},
        { data:"name"},
        { data:"type"},
        { data:"pattern"},
        { data:"options"},
    ],
    select: {
        style:'multi',
        selector: 'td:first-child'
    },
    order: [[ 1, 'asc', 'asc', 'asc', null ]]
});
//Load patterns to display in the table
function loadPatterns() {
    $.ajax({
        type:"GET",
        url:"/data-profile/patterns/list",
        dataType   : "json",
        success: function(data) {

            table.clear();
            $.each(data.patterns, function(idx, obj) {
                if(data.patterns[idx]["selected"]) {
                    table.row.add({
                        "selected": "",
                        "name":data.patterns[idx]["name"],
                        "type":data.patterns[idx]["type"],
                        "pattern":data.patterns[idx]["pattern"],
                        "options":"<button class='btn btn-warning' onclick='editPattern(" + data.patterns[idx]['id'] + ")'>" +
                            "<i class='fa fa-pencil'></i></button> <button class='btn btn-primary' onclick='deletePattern(" +data.patterns[idx]['id']  +")'><i class='fa fa-trash'></i></button>",
                        "id": data.patterns[idx]["id"]
                    }).select()
                }
                else {
                    table.row.add({
                        "selected": "",
                        "name":data.patterns[idx]["name"],
                        "type":data.patterns[idx]["type"],
                        "pattern":data.patterns[idx]["pattern"],
                        "options":"<button class='btn btn-warning' onclick='editPattern(" + data.patterns[idx]['id'] + ")'>" +
                            "<i class='fa fa-pencil'></i></button> <button class='btn btn-primary' onclick='deletePattern(" +data.patterns[idx]['id']  +")'><i class='fa fa-trash'></i></button>",
                        "id": data.patterns[idx]["id"]
                    })
                }


            })
            table.draw();

        }
    })
}
//show edit pattern modal and get pattern
function editPattern(id) {
    $.ajax({
        type:"POST",
        url:"/data-profile/patterns/edit",
        data:{
            'id':id,
            'csrfmiddlewaretoken': $("#csrf_token").val()
        },
        dataType   : "json",
        success: function(data) {
            $("#pattern-name").val(data.pattern[0]["name"]);
            $("#pattern-type").val(data.pattern[0]["type"]);
            $("#pattern-pattern").val(data.pattern[0]["pattern"]);
            $("#pattern-id").val(data.pattern[0]['id'].toString());
            $("#patternModal").modal('show');
        }
    })
}
//when u click delete icon in the list
function deletePattern(id) {
    swal({
        title: "Are you sure?",
        icon: "warning",
        buttons: true,
        dangerMode: true,
    })
    .then((willDelete) => {
        if (willDelete) {
            $.ajax({
                type:"POST",
                url:"/data-profile/patterns/delete",
                data:{
                    'id':id,
                    'csrfmiddlewaretoken': $("#csrf_token").val()
                },
                dataType   : "json",
                success: function(data) {
                    swal("A pattern was deleted successfully", {
                        icon: "success",
                        buttons:false,
                        timer:1000
                    });
                    loadPatterns();
                }
            })

        }
    })


}
//Clear the form
function clearPatternForm() {
    $("#pattern-name").val("");
    $("#pattern-type").val("");
    $("#pattern-pattern").val("");
    $("#pattern-id").val("-1");
}
//Capture Modal add button and post data to the backend
function addNewPattern() {

    const form = $('#pattern-form')[0];
    if(form.checkValidity()) {
        const patterName = $("#pattern-name").val();
        const patternType = $("#pattern-type").val();
        const patternPattern = $("#pattern-pattern").val();

        const patternID = $("#pattern-id").val();
        $.ajax({
            type:"POST",
            url:"/data-profile/patterns/store",
            data:{
                'name':patterName,
                'type':patternType,
                'pattern':patternPattern,
                'id': parseInt(patternID),
                'csrfmiddlewaretoken': $("#csrf_token").val()
            },
            dataType   : "json",
            success: function(data) {
                $("#patternModal").modal('hide');
                clearPatternForm();
                loadPatterns()
                if(parseInt(patternID) == -1)
                    swal({ title:"Success!", text:"A New Pattern created successfully!", icon:"success", timer:1000, buttons: false});
                else
                    swal({ title:"Success!", text:"A pattern updated successfully!", icon:"success", timer:1000, buttons: false});
            },
            error: function(xhr, textStatus, errorThrown) {
                errorData = JSON.parse(xhr.responseText);
                if (errorData.error == "pattern") {
                    swal({ title:"Error!", text:"The pattern is invalid", icon:"error", timer:1000, buttons: false});
                }
            }
        })
    }
}

// Find selected pattern and post to the backend
function saveSelectedPattern() {
    const ids = $.map(table.rows({selected:true}).data(), function(item){
        return item["id"]
    })
    $.ajax({
            type:"POST",
            url:"/data-profile/patterns/store/select",
            data:{
                'selected':ids,
                'csrfmiddlewaretoken': $("#csrf_token").val()
            },
            dataType   : "json",
            success: function(data) {
                swal({ title:"Success!", text:"patterns are seelected successfully!", icon:"success", timer:1000, buttons: false});

            }
        })
}
//onInitial
$(document).ready(function () {
    // Basic table example
    loadPatterns();

    //Capture Pattern close Modal Event
    $("#patternModal").on("hidden.bs.modal", function () {
        clearPatternForm(); //clear the Form
    });


})



