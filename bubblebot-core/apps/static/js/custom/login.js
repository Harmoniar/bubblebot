$("#loginBtn").click(function () {

    let formData = {}
    // 将表单键值对数据添加进FormData对象
    $.each($('#loginForm').serializeArray(), function (index, obj) {
        formData[obj.name] = obj.value
    })
    formData["remember"] = $("#rememberCheckbox").prop("checked")
    formData["csrfmiddlewaretoken"] = $("#loginForm").attr("csrf-token")

    $.ajax({
        url: "",
        type: "post",
        data: formData,
        dataType: "json",
        success: function (res) {
            if (res.errcode == 0) {
                notify_simple('登录成功', res.info + "即将转入管理后台", 'success')
                setTimeout(function () {
                    window.location.href = res.data.next_url
                }, 1000)
            } else if (res.errcode == 1) {
                $.each(res.data, function (input_name, errmsg_obj) {
                    notify_simple('登录失败', errmsg_obj[0], 'danger')
                    let tagId = "#id_" + input_name
                    $(tagId).addClass('is-invalid error-shadow')
                })
            } else {
                notify_simple('登录失败', res.info, 'danger')
            }
        }
    })
})

$("input").focus(function () {
    $(this).removeClass('is-invalid error-shadow')
})