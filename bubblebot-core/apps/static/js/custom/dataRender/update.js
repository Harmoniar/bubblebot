function cleanUpdateModal(speed) {
    if (speed == "fast") {
        $("#updateModalBody").empty()
    } else if (speed == "slow") {
        setTimeout(function () {
            $("#updateModalBody").empty()
        }, 200)
    } else if (!isNaN(speed)) {
        setTimeout(function () {
            $("#updateModalBody").empty()
        }, speed)
    }
}

function updateModalSetLoadAction() {
    $("#updateModalBody").html('<div class="text-center"><div class="spinner-border text-primary load-align mr-1"></div>正在努力加载数据中，请稍等...</div>')
}

function submitUpdateModalDataAction(updateData) {
    $.ajax({
        url: $("#renderData").attr("update-url"),
        type: "post",
        data: updateData,
        dataType: "json",
        traditional: true,
        success: function (res) {
            if (res.errcode == 0) {
                notify_simple('更新成功', res.info, 'success')
                $('#updateModal').modal('hide')
                cleanUpdateModal("slow")
                let page_index = parseInt($("#paginationList").data("current_index"))
                if (page_index) {
                    queryAction(page_index)
                }
            } else if (res.errcode == 1) {
                $.each(res.data, function (input_name, errmsg_obj) {
                    notify_simple('更新失败', errmsg_obj[0], 'danger')
                    let tagId = "#id_" + input_name
                    $(tagId).addClass('is-invalid error-shadow')
                })
            } else {
                notify_simple('更新失败', res.info, 'danger')
                $('#updateModal').modal('hide')
                cleanUpdateModal("slow")
            }
        }
    })
}


$(document).ready(function () {

    $("#displayTableBody").on("click", ".row-btn-update", function () {
        let dataId = $(this).parent().parent().attr("data-id")
        queryUpdateModalDataAction(dataId)
    })
    $("#cancelUpdateBtn").click(function () {
        cleanUpdateModal("slow")
    })

})