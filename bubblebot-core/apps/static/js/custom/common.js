// ======================================================
// string.format() 方法
// ======================================================

String.prototype.replaceAll = function (exp, newStr) {
    return this.replace(new RegExp(exp, "gm"), newStr);
};


String.prototype.format = function (args) {
    var result = this;
    if (arguments.length < 1) {
        return result;
    }
    var data = arguments; // 如果模板参数是数组
    if (arguments.length == 1 && typeof (args) == "object") {
        // 如果模板参数是对象
        data = args;
    }
    for (var key in data) {
        var value = data[key];
        if (undefined != value) {
            result = result.replaceAll("\\{" + key + "\\}", value);
        }
    }
    return result;
}

// ======================================================
// sleep() 函数
// ======================================================

function sleep(delay) {
    var start = (new Date()).getTime();
    while ((new Date()).getTime() - start < delay) {
        continue;
    }
}

// ======================================================
// notify()函数的封装
// ======================================================

function notify_simple(title, message, type) {
    $.notify({
        title: '<strong>{title}</strong>'.format({
            title: title
        }),
        message: message
    }, {
        type: type,
        placement: {
            from: "top",
            align: "center"
        },
        timer: 500,
        animate: {
            enter: 'animated zoomIn',
            exit: 'animated zoomOut'
        }
    })
}


// 初始化tooltip
function initTooltip() {
    $('[data-toggle="tooltip"]').tooltip()
}



$(document).ready(function () {
    initTooltip()

    // ajaxSetup()
    $.ajaxSetup({
        complete: function (res) {
            if (res.status !== 200) {
                notify_simple('请求失败', '请刷新重试', 'danger')
            }
        }
    })

    $("body").on("focus", "input", function () {
        $(this).removeClass('is-invalid error-shadow')
    })

    $("body").on("focus", "textarea", function () {
        $(this).removeClass('is-invalid error-shadow')
    })

    $("body").on("focus", "select", function () {
        $(this).removeClass('is-invalid error-shadow')
    })

})