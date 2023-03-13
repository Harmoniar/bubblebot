// ======================================================
// 清空表格体
//  1. displayTableBody
// ======================================================

function cleanTable() {
    $("#displayTableBody").empty()
}

// ======================================================
// 表格展示正在加载数据
//  1. displayTableBody
// ======================================================

function tableSetLoadAction() {
    $("#displayTableBody").html('<tr><td colspan="5" class="text-center text-muted"><div class="spinner-border text-primary load-align mr-1"></div>正在努力加载数据中，请稍等...</td></tr>')
}

// ======================================================
// 表格展示没有找到匹配的记录，同时隐藏分页信息与分页器
//  1. displayTableBody
//  2. pagerLeftDiv
//  3. pagerRightDiv
// ======================================================

function tableSetNotFound() {
    $("#displayTableBody").html('<td colspan="5" class="text-center">没有找到匹配的记录</td>')
    $("#pagerLeftDiv").addClass("not-display")
    $("#pagerRightDiv").addClass("not-display")
}


// ======================================================
// 渲染分页信息函数
//  1. pagerLeftDiv
//  2. pagerInfoSpan
// ======================================================

function renderDataToPagerInfo(queriedData) {
    let pagerInfo = "第 {current_row_min} 到 {current_row_max} 条，共 {total_row_num} 条记录。".format({
        current_row_min: queriedData.current_row_range[0],
        current_row_max: queriedData.current_row_range[1],
        total_row_num: queriedData.total_row_num
    })
    $("#pagerLeftDiv").removeClass("not-display")
    $("#pagerInfoSpan").text(pagerInfo)
}

// ======================================================
// 渲染分页器函数
//  1. pagerRightDiv
//  2. paginationList
// ======================================================

function renderDataToPagination(queriedData) {

    let paginationMaxEleNum = 7
    let paginationMaxEleNumHelf = (paginationMaxEleNum - 1) / 2
    let paginationEleHtml = new Array()

    // 计算页码
    if (queriedData.total_page_num <= paginationMaxEleNum) {
        var pager_start = 1
        var pager_end = queriedData.total_page_num
    } else {
        if (queriedData.current_page_num <= paginationMaxEleNumHelf) {
            var pager_start = 1
            var pager_end = paginationMaxEleNum
        } else {
            if ((queriedData.current_page_num + paginationMaxEleNumHelf) > queriedData.total_page_num) {
                var pager_start = queriedData.total_page_num - paginationMaxEleNum
                var pager_end = queriedData.total_page_num
            } else {
                var pager_start = queriedData.current_page_num - paginationMaxEleNumHelf
                var pager_end = queriedData.current_page_num + paginationMaxEleNumHelf
            }
        }
    }

    // 添加首页和上一页标签
    if (queriedData.has_previous) {
        var eleHtml = '<li class="page-item" page-index="{start_page_index}"><a class="page-link"><span>&laquo;</span></a></li><li class="page-item" page-index="{page_index}"><a class="page-link"><span>‹</span></a></li>'.format({
            start_page_index: 1,
            page_index: queriedData.current_page_num - 1
        })
    } else {
        var eleHtml = '<li class="page-item disabled"><a class="page-link"><span>&laquo;</span></a></li><li class="page-item disabled"><a class="page-link"><span>‹</span></a></li>'
    }
    paginationEleHtml.push(eleHtml)

    // 添加页码标签
    for (let i = pager_start; i <= pager_end; i++) {
        if (i == queriedData.current_page_num) {
            var eleHtml = '<li class="page-item active" page-index="{page_index}"><a class="page-link">{page_index}</a></li>'.format({
                page_index: i
            })
        } else {
            var eleHtml = '<li class="page-item" page-index="{page_index}"><a class="page-link">{page_index}</a></li>'.format({
                page_index: i
            })
        }
        paginationEleHtml.push(eleHtml)
    }

    // 添加尾页和下一页标签
    if (queriedData.has_next) {
        var eleHtml = '<li class="page-item" page-index="{page_index}"><a class="page-link"><span>›</span></a></li><li class="page-item" page-index="{start_page_index}"><a class="page-link"><span>&raquo;</span></a></li>'.format({
            page_index: queriedData.current_page_num + 1,
            start_page_index: queriedData.total_page_num
        })
    } else {
        var eleHtml = '<li class="page-item disabled"><a class="page-link"><span>›</span></a></li><li class="page-item disabled"><a class="page-link"><span>&raquo;</span></a></li>'
    }
    paginationEleHtml.push(eleHtml)

    // 如果页数大于1则显示分页器，否则不显示
    if (queriedData.total_page_num <= 1) {
        $("#pagerRightDiv").addClass("not-display")
    } else {
        $("#pagerRightDiv").removeClass("not-display")
    }
    $("#paginationList").html(paginationEleHtml.join(""))
}

// ======================================================
// 查询动作
//  1. queryForm：需要填写action属性(请求路径) 和 method属性(请求方法)
//  2. perPageNumSelect
//  3. 后端返回的数据格式需要是: 
//         {
//             "errcode": int, 
//             "info": str, 
//             "data": {{
//                 "total_row_num": int, 
//                 "total_page_num": int, 
//                 "total_page_range": list, 
//                 "current_row_range": list, 
//                 "current_page_num": int, 
//                 "has_next": bool, 
//                 "has_previous": bool, 
//                 "current_page_data": list,
//             }}
//         }
// ======================================================

function queryAction(page_index = 1) {
    tableSetLoadAction()

    let queryData = {}
    $.each($('#queryForm').serializeArray(), function (index, obj) {
        if (obj.value) {
            queryData[obj.name] = obj.value
        }
    })
    queryData["page_index"] = page_index
    queryData["per_page_num"] = $('#perPageNumSelect').val()

    $.ajax({
        url: $('#queryForm').attr("action"),
        type: $('#queryForm').attr("method"),
        data: queryData,
        dataType: 'json',
        success: function (res) {
            if (res.errcode == 0) {
                let queriedData = res.data
                if (typeof (queriedData) != "object") {
                    tableSetNotFound()
                    return false;
                }

                $("#paginationList").data("current_index", queriedData.current_page_num)

                if (queriedData.total_row_num == 0) {
                    tableSetNotFound()
                    return false;
                }

                cleanTable()
                renderDataToTable(queriedData)
                renderDataToPagerInfo(queriedData)
                renderDataToPagination(queriedData)

            } else if (res.errcode == 1) {
                $.each(res.data, function (input_name, errmsg_obj) {
                    notify_simple('查询失败', errmsg_obj[0], 'danger')
                    let tagId = "#id_" + input_name
                    $(tagId).addClass('is-invalid error-shadow')
                })
            } else {
                notify_simple('查询失败', res.info, 'danger')
            }
        }
    })
}

// ======================================================
// 初始化命令
//  1. queryBtn
//  2. paginationList
//  3. perPageNumSelect
//  4. flushBtn
// ======================================================
$(document).ready(function () {
    queryAction()
    $("#queryBtn").click(function () {
        queryAction()
    })
    $("#paginationList").on("click", "li", function () {
        let page_index = parseInt($(this).attr("page-index"))
        if (page_index) {
            queryAction(page_index)
        }
    })
    $("#perPageNumSelect").change(function () {
        queryAction()
    })
    $("#flushBtn").click(function () {
        let page_index = parseInt($("#paginationList").data("current_index"))
        if (page_index) {
            queryAction(page_index)
        }
    })
})