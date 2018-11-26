from seed.drives.email import send_email


def send_active_email(to_mail, active_url, redirect_url):
    """ 发送激活邮件
    """
    title = '新用户激活'
    mail_context = """
        亲爱的用户:
            感谢你使用Seed自定义报表系统，请点击以下链接激活用户:
            {active_url}?redirect_url={redirect_url}
            此链接24小时之后失效，请尽快激活邮箱。
        Seed团队
    """.format(active_url=active_url, redirect_url=redirect_url)
    print(mail_context)
    send_email(to_mail, title, mail_context)


def send_reset_password_email(to_mail, active_url, redirect_url):
    """ 发送重置密码邮件
    """
    title = '密码重置'
    mail_context = """
        亲爱的用户:
            你的密码重置连接如下:
            {active_url}?redirect_url={redirect_url}
            此链接24小时之后失效，请尽快点击重置密码。
        Seed团队
    """.format(active_url=active_url, redirect_url=redirect_url)
    print(mail_context)
    send_email(to_mail, title, mail_context)
