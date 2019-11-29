


import gurobi_MRCPSP
import Gantt_chart_draw

def main(file):
    f_CN = "./data/CNfks.xlsx"
    f_O = "./data/Ofs.xlsx"
    qfs = "./data/qfs.xlsx"
    n=0
    # M=[1, 3, 3, 3, 1, 3, 2, 3, 2, 2, 3, 2, 3, 2, 3, 1]
    # starttime=[0, 12, 2, 4, 35, 27, 42, 44, 55, 54, 67, 43, 64, 78, 53, 91]
    f_p = file
    ins = gurobi_MRCPSP.Instance()
    ins.loadData(file_project=f_p, file_CNfks=f_CN, file_Ofs=f_O, file_qfs=qfs)


    start,finish=ins.Gurobi_RSPSP_J14()
    Gantt_chart_draw.Gantt_chart(start,finish)

if __name__ == '__main__':
    main(file="./data/j141_8.mm")