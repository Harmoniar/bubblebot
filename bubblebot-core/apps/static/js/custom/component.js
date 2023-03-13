// 展开并激活对应模块的菜单
$("#systemManageCollapse").collapse('show')
$("#componentSidebar").addClass("active")

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
        let rowHtml = "<tr>\
        <td style='width: 80px;'>{index}</td>\
        <td style='width: 120px;'>{component_id}</td>\
        <td style='width: 120px;'>{component_role}</td>\
        <td style='width: 120px;'>{component_ip}</td>\
        <td style='width: 120px;'>{component_status}</td>\
        <td style='width: 120px;'>{last_report_time}</td>\
        <td style='width: 120px;'>{create_time}</td>\
        </tr>"
            .format({
                index: start_index_num,
                component_id: data.component_id,
                component_role: data.component_role,
                component_ip: data.component_ip,
                component_status: data.component_status,
                last_report_time: data.last_report_time,
                create_time: data.create_time,
            })
        tableRowHtml.push(rowHtml)
        start_index_num += 1
    })
    $("#displayTableBody").html(tableRowHtml.join(""))
}