# Author: c10udlnk(https://github.com/c10udlnk)
# Author's blog: https://c10udlnk.top/
# Github repo: https://github.com/c10udlnk/hexo-T1meM4chine
# Enjoy it!

from T1meM4chine_api import *
import time

if __name__ == '__main__':
    my_name = input(setColor("请输入你的Github用户名：", 11))
    year = str(input(setColor("想看哪一年的年度报告（纯数字喔）：", 11)))
    printMenu()

    my_blog_url = "https://" + my_name + ".github.io"
    atom_link = my_blog_url + "/atom.xml"
    api_header = "https://api.github.com/repos/" + my_name + "/" + my_name + ".github.io"

    homepage_info, all_page_info = parseAtomXML(atom_link)
    homepage_info.update(parseHeader(api_header))
    makeAnnualReview(homepage_info, all_page_info, year)