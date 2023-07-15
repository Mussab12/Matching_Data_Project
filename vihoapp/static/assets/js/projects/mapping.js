(function($) {
    var original = '';
    getDataSource();
    table_datasource_list = $('#table_datasource_list').DataTable({
        "processing": true,
        // "language": {
        //     processing: "<span class='fa-stack fa-lg' style='z-index: 60000;width: 200px'>\n\
        //                 <i class='fa fa-spinner fa-spin fa-stack-2x fa-fw' ></i>\n\
        //                 </span><span style='margin-right: 50px; display: inline-block'>&nbsp;&nbsp;&nbsp;&nbsp;Processing ...</span>"
        // },
        
        "serverSide": true,

        dom: 'Btip',

        info: true,
        "ajax": '/mapping/datasource/list',

        "columns": [
            {
                "data": "name"
            },
            {
                "data": null,
                render: function (val, beta, row) {
                    return '<button id="btn_datasource_edit" type="button" class="btn btn-sm btn-warning">Edit</button>' + '&nbsp;&nbsp' +
                        '<button id="btn_datasource_delete" type="button" class="btn btn-danger">Delete</button>';
                }
            }
        ],
        serverParams: function (p) {
        }
    });
    table_datasource_list.on('click', '#btn_datasource_delete', function() {
        var row = $(this).closest('tr');
        var datasource_data = table_datasource_list.row(row).data();
        var datasource_id = datasource_data['id'];
        $.ajax({
            url: '/mapping/datasource/delete',
            type: 'POST',
            dataType: 'json',
            headers: {
                'csrfmiddlewaretoken': `{{ csrf_token }}`
            },
            data: {
                'id': datasource_id
            },
            success:function(data) {
                if (data['success'] == true) {
                    alert("Deleted");
                    table_datasource_list.draw();
                }
            }
        });
    });
    
    table_datasource_list.on('click', '#btn_datasource_edit', function() {
        var row = $(this).closest('tr');
        var datasource_data = table_datasource_list.row(row).data();
        $('#modal_title_datasource').text('Edit datasource');
        $("#datasource_name").val(datasource_data['name']);
        $("#datasource_error").css('display', 'none');
        $('#datasource_id').text(datasource_data['id'])
        $("#modal_datasource").modal('show');
    });
    //datasource modal show
    $("#btn_datasource_add").click(function() {
        $("#modal_title_datasource").text("Add datasource");
        $("#datasource_name").val('');
        $("#datasource_error").css('display', 'none');
        $("#modal_datasource").modal('show');
    });
    //add datasource
    $("#btn_datasource_save").click(function() {
        var datasource_id = $('#datasource_id').text();
        var datasource_name = $("#datasource_name").val();
        if (datasource_name == '') {
            $("#datasource_error").text('Please input the name');
            $("#datasource_error").css('display', 'block');
            return false;
        }
        $.ajax({
            url: '/mapping/datasource/add',
            type: 'POST',
            dataType: 'json',
            headers: {
                'csrfmiddlewaretoken': `{{ csrf_token }}`
            },
            data: {
                'id': datasource_id,
                'name': datasource_name
            },
            success:function(data) {
                if (data['success'] == false) {
                    if (data['datasource_error'] == 1) {
                        $('#datasource_error').text('Name already exists!');
                        $('#datasource_error').css('display', 'block');
                    }
                }
                else {
                    $("#modal_datasource").modal('hide');
                    table_datasource_list.draw();
                }
            }
        });
    });
    $("#datasource_name").on('input', function() {
        $("#datasource_error").css('display', 'none');
    });
    //mapping crud table
    table_mapping_crud = $('#table_mapping_crud').DataTable({
        "processing": true,
        "serverSide": false,
        dom: 'Btip',
        "pageLength": 10,
        info: true,
    });
    table_mapping_crud.on('click','.btn_mapping_edit', function() {
        var row = $(this).closest('tr');
        var data = table_mapping_crud.row(row).data();
        original = data[0];
        $('#original_name').val(data[1]);
        $('#mapping_headers_name').val(data[0]);
        $('#modal_mapping').modal('show');
    });
    $('#btn_mapping_headers_save').click(function() {
        var val = $('#mapping_headers_name').val();
        if (original == val) {
            $('#modal_mapping').modal('hide');
            return true;
        }
        else {
            $.ajax({
                url: '/mapping/header/edit',
                type: 'POST',
                dataType: 'json',
                headers: {
                    'csrfmiddlewaretoken': `{{ csrf_token }}`
                },
                data: {
                    'original_data': original,
                    'current_data': val
                },
                success:function(data) {
                    if (data['success'] == true) {
                        alert("Changed!");
                        $('modal_mapping').modal('hide');
                    }
                }
            });
        }
    });
    table_mapping_crud.on('click', '.btn_mapping_delete', function(){
        var row = $(this).closest('tr');
        var data = table_mapping_crud.row(row).data();
        original_data = data[1];
        mapping_headers_data = data[0];
        $.ajax({
            url: '/mapping/header/edit',
            type: 'POST',
            dataType: 'json',
            headers: {
                'csrfmiddlewaretoken': `{{ csrf_token }}`
            },
            data: {
                'original_data': mapping_headers_data,
                'current_data': original_data
            },
            success:function(data) {
                if (data['success'] == true) {
                    alert("Deleted!");
                    table_mapping_crud.rows(row).remove().draw(false);
                }
            }
        });
    });
})(jQuery);

function getDataSource() {
    $.ajax({
        url: '/mapping/datasource/all',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            datasource_list = data['data'];
            // var str = "<optgroup label='Data Source'></optgroup>";
            var str = '<option value="" selected disabled hidden>Select a DataSource</option>';
            // str += '{% comment %} <option value="">Select File Type</option> {% endcomment %}'
            datasource_list.forEach((row_data, i)=> {
                str += '<option value="' + row_data['id'] + '">' + row_data['name'] + '</option>';
            });
            // str += "</optgroup>";
            $('#list_datasource').html(str);
        }
    });
}