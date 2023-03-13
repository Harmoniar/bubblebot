// 激活对应模块的菜单
$("#robotTimingSidebar").addClass("active")


// =============================================================================================
// 渲染数据到表格
//  1. displayTableBody
//  PS: 1. 因为每个模块的data都不一样，所以要自己定义
//      2. data-render脚本需要用到该函数，所以要定义在其之前
//      3. data-render脚本会将查询到的data数据传入给该函数
// =============================================================================================

function renderDataToTable(queriedData) {
    let tableRowHtml = new Array()
    var start_index_num = queriedData.current_row_range[0]
    $.each(queriedData.current_page_data, function (index, data) {
        let actionHtml = "\
        <button data-toggle='modal' href='#updateModal' class='btn btn-primary text-center row-btn row-btn-update'><i class='fas fa-pen-to-square mr-1'></i>配置</button>\
        <button class='btn btn-danger text-center row-btn row-btn-delete'><i class='fas fa-xmark mr-1'></i>删除</button>\
        "

        let rowHtml = "<tr data-id='{data_id}'>\
        <td style='width: 40px;'><input type='checkbox'></td>\
        <td style='width: 80px;'>{index}</td>\
        <td style='width: 120px;'>{robot_id}</td>\
        <td style='width: 120px;'>{timing_function_id}</td>\
        <td style='width: 120px;'>{timing_function_name}</td>\
        <td style='width: 120px;'>{timing_cron}</td>\
        <td style='width: 120px;'>{timing_status}</td>\
        <td style='width: 120px;' title='{explain}'>{explain}</td>\
        <td style='width: 145px;'>{action}</td>\
        </tr>"
            .format({
                index: start_index_num,
                data_id: data.robot_id + "==:::==" + data.timing_function_id,
                robot_id: data.robot_id,
                timing_function_id: data.timing_function_id,
                timing_function_name: data.timing_function_name,
                timing_cron: data.timing_cron,
                timing_status: data.timing_status,
                explain: data.explain,
                action: actionHtml
            })
        tableRowHtml.push(rowHtml)
        start_index_num += 1
    })
    $("#displayTableBody").html(tableRowHtml.join(""))
}


// 更新 ====================================================================

function queryUpdateModalDataAction(dataId) {
    updateModalSetLoadAction()
    $.ajax({
        url: $("#renderData").attr("update-url"),
        type: "get",
        data: {
            id: dataId
        },
        success: function (res) {
            if (res.errcode == 0) {
                cleanUpdateModal("fast")
                $("#updateModalBody").html(res.data.html)
                initTooltip()
            } else {
                notify_simple('查询失败', res.info, 'danger')
                $('#updateModal').modal('hide')
            }
        }
    })
}

$(document).ready(function () {
    $("#confirmUpdateBtn").click(function () {
        if ($("#updateForm").length < 1) {
            notify_simple('更新失败', '数据暂未加载成功', 'danger')
            return false;
        }
        let updateData = {}
        $.each($('#updateForm').serializeArray(), function (index, obj) {
            if (obj.value) {
                updateData[obj.name] = obj.value
            }
        })
        updateData["robot_timing_function_id"] = $("#updateForm").attr("robot-timing-function-id")
        updateData["csrfmiddlewaretoken"] = $("#renderData").attr("csrf-token")
        submitUpdateModalDataAction(updateData)
    })
})