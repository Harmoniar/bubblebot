// 激活对应模块的菜单
$("#robotSidebar").addClass("active")


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

        let rowHtml = "<tr data-id='{robot_id}'>\
        <td style='width: 40px;'><input type='checkbox'></td>\
        <td style='width: 80px;'>{index}</td>\
        <td style='width: 120px;'>{robot_id}</td>\
        <td style='width: 120px;'>{robot_name}</td>\
        <td style='width: 120px;'>{master_id}</td>\
        <td style='width: 120px;'>{robot_status}</td>\
        <td style='width: 120px;' title='{run_time}'>{run_time}</td>\
        <td style='width: 120px;' title='{comment}'>{comment}</td>\
        <td style='width: 145px;'>{action}</td>\
        </tr>"
            .format({
                index: start_index_num,
                robot_id: data.robot_id,
                robot_name: data.robot_name,
                master_id: data.master_id,
                robot_status: data.robot_status,
                run_time: data.run_time,
                comment: data.comment,
                action: actionHtml
            })
        tableRowHtml.push(rowHtml)
        start_index_num += 1
    })
    $("#displayTableBody").html(tableRowHtml.join(""))
    initTooltip()
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
                updateModalPrefixTriggerChangeAction()
                updateModalGroupPermitChangeAction()
                initTooltip()
            } else {
                notify_simple('查询失败', res.info, 'danger')
                $('#updateModal').modal('hide')
            }
        }
    })
}

function updateModalPrefixTriggerChangeAction() {
    if ($("[name=trigger_mode_update]:first").first().prop("checked")) {
        $("#id_command_prefix_update").parent().removeClass("not-display")
    } else {
        $("#id_command_prefix_update").parent().addClass("not-display")
    }
}


function updateModalGroupPermitChangeAction() {
    // if ($("#id_group_permit_mode_update").val() == "0") {
    //     $("#id_group_whitelist_update").parent().addClass("not-display")
    //     $("#id_group_blacklist_update").parent().addClass("not-display")
    // }
    if ($("#id_group_permit_mode_update").val() == "1") {
        $("#id_group_whitelist_update").parent().removeClass("not-display")
        $("#id_group_blacklist_update").parent().addClass("not-display")
    } else if ($("#id_group_permit_mode_update").val() == "2") {
        $("#id_group_blacklist_update").parent().removeClass("not-display")
        $("#id_group_whitelist_update").parent().addClass("not-display")
    }
}


$(document).ready(function () {

    $("#confirmUpdateBtn").click(function () {
        if ($("#updateForm").length < 1) {
            notify_simple('更新失败', '数据暂未加载成功', 'danger')
            return false;
        }
        let listFieldNameArray = ["listen_msg_type_update", "trigger_mode_update"]
        let updateData = {}
        $.each($('#updateForm').serializeArray(), function (index, obj) {
            if (obj.value) {
                if (listFieldNameArray.indexOf(obj.name) >= 0) {
                    if (updateData[obj.name] == undefined) {
                        updateData[obj.name] = []
                    }
                    updateData[obj.name].push(obj.value)
                } else {
                    updateData[obj.name] = obj.value
                }
            }
        })
        updateData["original_robot_id"] = $("#updateForm").attr("original-robot-id")
        updateData["csrfmiddlewaretoken"] = $("#renderData").attr("csrf-token")
        submitUpdateModalDataAction(updateData)
    })

    $("#updateModalBody").on("change", "#id_group_permit_mode_update", updateModalGroupPermitChangeAction)
    $("#updateModalBody").on("change", "[name=trigger_mode_update]:first", updateModalPrefixTriggerChangeAction)

})