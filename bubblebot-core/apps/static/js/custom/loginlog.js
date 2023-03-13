// 展开并激活对应模块的菜单
$("#systemSettingsCollapse").collapse('show')
$("#loginLogSidebar").addClass("active")


// ======================================================
// 日期框默认设置为当天时间
// ======================================================

// function setCurrentDate() {
//     let time = new Date()
//     let day = ("0" + time.getDate()).slice(-2)
//     let month = ("0" + (time.getMonth() + 1)).slice(-2)
//     let today = time.getFullYear() + "-" + (month) + "-" + (day)
//     $("input[type='date']").val(today)
// }


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
        <td style='width: 120px;'>{login_ip}</td>\
        <td style='width: 120px;'>{login_location}</td>\
        <td style='width: 120px;'>{login_time}</td>\
        <td style='width: 120px;'>{login_result}</td>\
        </tr>"
            .format({
                index: start_index_num,
                login_ip: data.login_ip,
                login_location: data.login_location,
                login_time: data.login_time,
                login_result: data.login_result,
            })
        tableRowHtml.push(rowHtml)
        start_index_num += 1
    })
    $("#displayTableBody").html(tableRowHtml.join(""))
}