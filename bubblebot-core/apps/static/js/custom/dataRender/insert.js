// 添加====================================================================

function insertAction() {
    let insertData = {}
    $.each($('#insertForm').serializeArray(), function (index, obj) {
        if (obj.value) {
            insertData[obj.name] = obj.value
        }
    })
    insertData["csrfmiddlewaretoken"] = $("#renderData").attr("csrf-token")
    $.ajax({
        url: $("#renderData").attr("insert-url"),
        type: "post",
        data: insertData,
        dataType: "json",
        traditional: true,
        success: function (res) {
            if (res.errcode == 0) {
                notify_simple('添加成功', res.info, 'success')
                $('#insertModal').modal('hide')
                $("#insertForm").trigger("reset")
                let page_index = parseInt($("#paginationList").data("current_index"))
                if (page_index) {
                    queryAction(page_index)
                }
            } else if (res.errcode == 1) {
                $.each(res.data, function (input_name, errmsg_obj) {
                    notify_simple('添加失败', errmsg_obj[0], 'danger')
                    let tagId = "#id_" + input_name
                    $(tagId).addClass('is-invalid error-shadow')
                })
            } else {
                notify_simple('添加失败', res.info, 'danger')
                $('#insertModal').modal('hide')
                $("#insertForm").trigger("reset")
            }
        }
    })
}

$(document).ready(function () {
    
    $("#cancelInsertBtn").click(function () {
        $("#insertForm").trigger("reset")
    })

    $("#confirmInsertBtn").click(function () {
        insertAction()
    })


})