// 展开并激活对应模块的菜单
$("#systemSettingsCollapse").collapse('show')
$("#personalSidebar").addClass("active")


// 头像上传实时展示
$("#id_avatar").change(function () {
    let fileReader = new FileReader()
    let fileData = $(this)[0].files[0]
    fileReader.readAsDataURL(fileData)
    fileReader.onload = function () {
        $("#avatarImg").attr("src", fileReader.result)
    }
})

// 提交按钮
$("#submitBtn").click(function () {

    let formData = new FormData()
    // 将表单键值对数据添加进FormData对象
    $.each($('#personalForm').serializeArray(), function (index, obj) {
        formData.append(obj.name, obj.value)
    })
    formData.append('avatar', $('#id_avatar')[0].files[0])
    formData.append("csrfmiddlewaretoken", $("#personalForm").attr("csrf-token"))

    $.ajax({
        url: '',
        type: 'post',
        data: formData,
        dataType: 'json',
        contentType: false,
        processData: false,
        success: function (res) {
            if (res.errcode == 0) {
                notify_simple('修改成功', res.info + "即将刷新页面", 'success')
                setTimeout(function () {
                    window.location.reload()
                }, 2000)

            } else if (res.errcode == 1) {

                $.each(res.data, function (input_name, errmsg_obj) {
                    notify_simple('修改失败', errmsg_obj[0], 'danger')
                    let tagId = "#id_" + input_name
                    $(tagId).addClass('is-invalid error-shadow')
                })
            } else {
                notify_simple('修改失败', res.info, 'danger')
            }
        }
    })
})

$("input").focus(function () {
    $(this).removeClass('is-invalid error-shadow')
})