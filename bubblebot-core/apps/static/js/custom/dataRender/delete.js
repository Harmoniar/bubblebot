// 删除====================================================================

function deleteAction(dataIdArray) {
    // 请求删除数据
    swal("删除数据", "确定要删除所选的数据吗？可不能后悔哟！", "error", {
        buttons: ["取消", "确认"],
    }).then(value => {
        if (value) {
            $.ajax({
                url: $("#renderData").attr("delete-url"),
                type: "post",
                data: {
                    data_id_list: dataIdArray,
                    csrfmiddlewaretoken: $("#renderData").attr("csrf-token")
                },
                dataType: "json",
                traditional: true,
                success: function (res) {
                    if (res.errcode == 0) {
                        notify_simple('删除成功', res.info, 'success')
                    } else {
                        notify_simple('删除失败', res.info, 'danger')
                    }
                    let page_index = parseInt($("#paginationList").data("current_index"))
                    if (page_index) {
                        queryAction(page_index)
                    }
                }
            })
        }
    })
}

$(document).ready(function () {

    $("#btSelectAllInput").click(function () {
        if ($(this).prop("checked")) {
            $("#displayTableBody input[type='checkbox']").prop("checked", true)
        } else {
            $("#displayTableBody input[type='checkbox']").prop("checked", false)
        }
    })


    $("#displayTableBody").on("click", ".row-btn-delete", function () {
        let dataIdArray = [$(this).parent().parent().attr("data-id")]
        deleteAction(dataIdArray)
    })

    $("#headerDeleteBtn").click(function () {
        let dataIdArray = new Array()
        let checkedRow = $("#displayTableBody input[type='checkbox']")
        $.each(checkedRow, function (index, row) {
            if ($(row).prop("checked")) {
                let rowDataId = $(row).parent().parent().attr("data-id")
                dataIdArray.push(rowDataId)
            }
        })
        deleteAction(dataIdArray)
    })


})