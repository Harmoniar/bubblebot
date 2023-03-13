// 切换收缩侧边栏
$('.sidebar-toggler').on('click', function () {
    $('.sidebar').toggleClass('shrink show');
    $('.page-holder').toggleClass('page-sidebar-shrink');
});

// 退出登录
$("#logoutBtn").click(function () {
    swal("退出登录", "你确定要退出登录吗？", "warning", {
        buttons: ["取消", "确认"],
    }).then(value => {
        if (value) {
            $.ajax({
                url: $(this).attr("url"),
                type: 'get',
                success: function (res) {
                    window.location.reload()
                }
            })
        }
    })
})