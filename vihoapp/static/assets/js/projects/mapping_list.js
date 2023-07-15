(function($) {
    table_category_list = $('#table_category_list').DataTable({
        "processing": true,
        // "language": {
        //     processing: "<span class='fa-stack fa-lg' style='z-index: 60000;width: 200px'>\n\
        //                 <i class='fa fa-spinner fa-spin fa-stack-2x fa-fw' ></i>\n\
        //                 </span><span style='margin-right: 50px; display: inline-block'>&nbsp;&nbsp;&nbsp;&nbsp;Processing ...</span>"
        // },
        
        "serverSide": true,

        dom: 'Btip',

        info: true,
        "ajax": '/mapping/category/list',

        "columns": [
            {
                "data": "name"
            },
            {
                "data": null,
                render: function (val, beta, row) {
                    return '<button id="btn_category_edit" type="button" class="btn btn-sm btn-warning">Edit</button>' + '&nbsp;&nbsp' +
                        '<button id="btn_category_delete" type="button" class="btn btn-danger">Delete</button>';
                }
            }
        ],
        serverParams: function (p) {
        }
    });
    table_category_list.on('click', '#btn_category_delete', function() {
        var row = $(this).closest('tr');
        var category_data = table_category_list.row(row).data();
        var category_id = category_data['id'];
        $.ajax({
            url: '/mapping/category/delete',
            type: 'POST',
            dataType: 'json',
            headers: {
                'csrfmiddlewaretoken': `{{ csrf_token }}`
            },
            data: {
                'id': category_id
            },
            success:function(data) {
                if (data['success'] == true) {
                    alert("Deleted");
                    table_category_list.draw();
                }
            }
        });
    });
    
    table_category_list.on('click', '#btn_category_edit', function() {
        var row = $(this).closest('tr');
        var category_data = table_category_list.row(row).data();
        $('#modal_title_category').text('Edit Category');
        $("#category_name").val(category_data['name']);
        $("#category_error").css('display', 'none');
        $('#category_id').text(category_data['id'])
        $("#modal_category").modal('show');
    });
    //category modal show
    $("#btn_category_add").click(function() {
        $("#modal_title_category").text("Add Category");
        $("#category_name").val('');
        $("#category_error").css('display', 'none');
        $("#modal_category").modal('show');
    });
    //add category
    $("#btn_category_save").click(function() {
        var category_id = $('#category_id').text();
        var category_name = $("#category_name").val();
        if (category_name == '') {
            $("#category_error").text('Please input the name');
            $("#category_error").css('display', 'block');
            return false;
        }
        $.ajax({
            url: '/mapping/category/add',
            type: 'POST',
            dataType: 'json',
            headers: {
                'csrfmiddlewaretoken': `{{ csrf_token }}`
            },
            data: {
                'id': category_id,
                'name': category_name
            },
            success:function(data) {
                if (data['success'] == false) {
                    if (data['category_error'] == 1) {
                        $('#category_error').text('Name already exists!');
                        $('#category_error').css('display', 'block');
                    }
                }
                else {
                    $("#modal_category").modal('hide');
                    table_category_list.draw();
                }
            }
        });
    });
    $("#category_name").on('input', function() {
        $("#category_error").css('display', 'none');
    });

    table_mapping_list = $('#table_mapping_list').DataTable({
        "processing": true,
        
        "serverSide": true,

        dom: 'Btip',

        info: true,
        "ajax": '/mapping/mapping/list',

        "columns": [
            {
                "data": "category_name"
            },
            {
                "data": "name"
            },
            {
                "data": "display_name"
            },
            {
                "data": null,
                render: function (val, beta, row) {
                    return '<button id="btn_mappinglist_edit" type="button" class="btn btn-sm btn-warning">Edit</button>' + '&nbsp;&nbsp' +
                        '<button id="btn_mappinglist_delete" type="button" class="btn btn-danger">Delete</button>';
                }
            }
        ],
        serverParams: function (p) {
        }
    });
    table_mapping_list.on('click', '#btn_mappinglist_delete', function() {
        var row = $(this).closest('tr');
        var mappinglist_data = table_mapping_list.row(row).data();
        var mappinglist_id = mappinglist_data['id'];
        $.ajax({
            url: '/mapping/mapping/delete',
            type: 'POST',
            dataType: 'json',
            headers: {
                'csrfmiddlewaretoken': `{{ csrf_token }}`
            },
            data: {
                'id': mappinglist_id
            },
            success:function(data) {
                if (data['success'] == true) {
                    alert("Deleted");
                    table_mapping_list.draw();
                }
            }
        });
    });
    table_mapping_list.on('click', '#btn_mappinglist_edit', function() {
        var row = $(this).closest('tr');
        var mapping_list = table_mapping_list.row(row).data();
        $('#modal_title_mappinglist').text('Edit Mapping List');
        $("#mappinglist_name").val(mapping_list['name']);
        $("#display_name").val(mapping_list['display_name']);
        $("#mappinglist_name_error").css('display', 'none');
        $("#display_name_error").css('display', 'none');
        $('#mappinglist_id').text(mapping_list['id'])
        $.ajax({
            url: '/mapping/category/all',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                category_list = data['data'];
                var str = '<option value="" selected disabled hidden>Select a Category</option>';
                category_list.forEach((row_data, i)=> {
                    str += '<option value="' + row_data['id'] + '">' + row_data['name'] + '</option>';
                });
                $('#category_list').html(str);
                $('#category_list').val(mapping_list['category_id']);
            }
        });
        $("#modal_mappinglist").modal('show');
    });
    $("#btn_mappinglist_add").click(function() {
        $("#modal_title_mappinglist").text("Add Mapping List");
        $("mappinglist_name").val('');
        $("#mappinglist_error").css('display', 'none');
        var category_list = [];
        $.ajax({
            url: '/mapping/category/all',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                category_list = data['data'];
                var str = '<option value="" selected disabled hidden>Select a Category</option>';
                category_list.forEach((row_data, i)=> {
                    str += '<option value="' + row_data['id'] + '">' + row_data['name'] + '</option>';
                });
                $('#category_list').html(str);
            }
        });
        $('#mappinglist_name').val('');
        $('#display_name').val('');
        $('#mappinglist_name_error').css('display', 'none');
        $('#display_name_error').css('display', 'none');
        $("#modal_mappinglist").modal('show');
    });
    $('#btn_mappinglist_save').click(function() {
        var mappinglist_id = $('#mappinglist_id').text();
        var category_id = $('#category_list').val();
        var mappinglist_name = $('#mappinglist_name').val();
        var display_name = $('#display_name').val();
        if (category_id == null) {
            alert('Please select the Category List');
            return false;
        }
        if (mappinglist_name == '') {
            $('#mappinglist_name_error').text('Please Enter the Mapping List Name');
            $('#mappinglist_name_error').css('display', 'block');
            return false;
        }
        if (display_name == '') {
            $('#display_name_error').text('Please Enter the Display Name');
            $('#display_name_error').css('display', 'block');
            return false;
        }
        $.ajax({
            url: '/mapping/mapping/add',
            type: 'POST',
            dataType: 'json',
            headers: {
                'csrfmiddlewaretoken': `{{ csrf_token }}`
            },
            data: {
                'mappinglist_id': mappinglist_id,
                'category_id': category_id,
                'mappinglist_name': mappinglist_name,
                'display_name': display_name
            },
            success:function(data) {
                if (data['success'] == true) {
                    $('#modal_mappinglist').modal('hide');
                    table_mapping_list.draw();
                } else {
                    if (data['mapping_error'] == 1) {
                        $('#display_name_error').text('Display Name already exist');
                        $('#display_name_error').css('display', 'block');
                    }
                }
            }
        });
    });
    $("#mappinglist_name").on('input', function() {
        $("#mappinglist_name_error").css('display', 'none');
    });
    $("#display_name").on('input', function() {
        $("#display_name_error").css('display', 'none');
    });
})(jQuery);