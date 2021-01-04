from T1meM4chine_api import *
import time

if __name__=='__main__':
    # -=-=-=将my_name修改为你的用户名-=-=-=
    my_name="c10udlnk"
    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    my_hexo_repo="https://github.com/"+my_name+"/"+my_name+".github.io"
    my_hexo_branch="/master"
    atom_link=my_hexo_repo+"/raw"+my_hexo_branch+"/atom.xml"
    api_header="https://api.github.com/repos/"+my_name+"/"+my_name+".github.io"
    homepage_info,all_page_info=parseAtomXML(atom_link)
    year=str(int(time.asctime(time.localtime())[-4:])-1)
    homepage_info.update(parseHeader(api_header))
    makeAnnualReview(homepage_info,all_page_info,year)