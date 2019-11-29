from gurobipy import *
import data_read_MRCPSP
import matplotlib.pyplot as plt
import  copy
import matplotlib.font_manager

matplotlib.rcParams["font.family"] = "Kaiti"
matplotlib.rcParams["font.size"] = 20



class Instance():
    def __init__(self):

        self.job_num_successors=[]
        self.job_predecessors = []
        self.job_successors=[]
        self.job_model_resource={1:{1:[0 for _ in range(8)],2:[0 for _ in range(8)],3:[0 for _ in range(8)]},16:{1:[0 for _ in range(8)],2:[0 for _ in range(8)],3:[0 for _ in range(8)]}}
        self.job_model_duration={1:{1:0,2:0,3:0},16:{1:0,2:0,3:0}}
        self.Lead_time_E=[2,3,2,4,2,3,4]
        self.Lead_time_0=[2.364793499419341, 3.590722183867771, 2.5540486141093632, 4.368226030629229, 2.316351827116401, 3.0796935154386236, 3.706033524317347]
        self.resource_capacity=[]
        self.number_job =None
        self.number_renewable_resources = None
        self.number_unrenewable_resources = None
        self.resource_capacity = None
        self.upper_bound=228
        self.CNfks={}
        self.Ofs=None
        self.qfs=None
        self.popSize=100
        self.k=4
        self.kk=8
        self.If=[3,3,2,4,3,2]
        self.choice_supplier=[]
        self.order_time=[]
        self.mate_pb=0.8
        self.mutate_pb=0.1

        self.best_ind=[]
        self.best_sup=[]
        self.time=[]
    def loadData(self,file_project,file_CNfks,file_Ofs,file_qfs):
        data_read_MRCPSP.dataStore(self, file_project)   #project info
        data_read_MRCPSP.read_CNfks(self,file_CNfks)     # per order cost
        data_read_MRCPSP.read_Ofs(self,file_Ofs)         # fix ordercost
        data_read_MRCPSP.read_qfs(self,file_qfs)         # resource quality

    def Gurobi_RSPSP_J14(self):
        # Set the upper bound Completion Time of the project
        # we set T=100 when you solve the J30 problem

        F=6 #numbers of materials
        S=7 #numbers of suppliers
        K=3 # interval of discount
        T=50 # project
        Mo=3 # number of model
        DL=15 # project complete t ime  line
        p1=12   #project delay cost
        p2=6    #project advance cost



        # Initial the gurobi model
        m = Model()
        #add variables xjt note that j activity start at time t
        x = m.addVars(self.number_job,Mo,T,vtype=GRB.BINARY, name='x')
        y = m.addVars(F, K,S, T, vtype=GRB.BINARY, name='y')
        # z = m.addVars(F, K,S, T,self.number_job,vtype=GRB.BINARY, name='z')
        Qfst = m.addVars(F,S, T, vtype=GRB.INTEGER, name='Qfst')

        # inventory constr
        Ift0=[[0 for _ in range(T)] for i in range(self.number_unrenewable_resources)]
        for re in range(self.number_unrenewable_resources):
            for t in range(10,T-10):    #项目开始前的预留时间10天
                use_unrenew=0
                for job in range(1,self.number_job-1):
                    for jm4 in range(Mo):
                        use_unrenew+=(self.job_model_resource[job+1][jm4+1][re+2])*x[job,jm4,t-1]
                L=0 #int(np.random.normal(5,0.5))
                Ift0[re][t]=Ift0[re][t-1]+sum(Qfst[re,s,t-L] for s in range(S))-use_unrenew

            for t2 in range(T):
                m.addConstr( Ift0[re][t2]>=sum(self.job_model_resource[j+1][jm+1][2+re]*x[j,jm,t2] for j in range(self.number_job) for jm in range(Mo)) ,name='inven'+str(0)+str(t2))

        #ordercost
        obj31=0
        for s in range(S):
            for f in range(F):
                for t in range(T):
                    if Qfst[f,s,t]>=1:
                         if Qfst[f,s,t]<=5:
                             obj31+=(self.Ofs.loc["f"+str(f+1)]["s"+str(s+1)]+self.CNfks["S"+str(s+1)].loc["f"+str(f+1)]["k1"]*Qfst[f,s,t])   #*y[f,k,s,t]
                         elif Qfst[f, s, t] <= 10:
                             obj31 += (self.Ofs.loc["f"+str(f+1)]["s"+str(s+1)]+ self.CNfks["S"+str(s+1)].loc["f"+str(f+1)]["k2"] * Qfst[f, s, t])  # *y[f,k,s,t]
                         elif Qfst[f, s, t] >= 10:
                             obj31 += (self.Ofs.loc["f"+str(f+1)]["s"+str(s+1)] + self.CNfks["S"+str(s+1)].loc["f"+str(f+1)]["k3"] * Qfst[f, s, t])

        #inventory cost
        obj33 = 0
        for re in range(self.number_unrenewable_resources):
            for t in range(T):
                obj33 += Ift0[re][t] * self.If[re]

        #delay or advance cost
        obj34=0
        for jm3 in range(Mo):
            for t in range(T):
                if t>=DL:
                    obj34+=(t-DL)*x[self.number_job-1,jm3,t]*p1
                else:
                    obj34+=(DL-t)*x[self.number_job-1,jm3,t]*p2
        obj3=obj31+obj33+obj34

        m.setObjective(obj3, GRB.MINIMIZE)  #成本


        # Constraint only can be done once
        for i in range(self.number_job):
            m.addConstr(sum(x[i,jm,t] for t in range(T) for jm in range(Mo))==1,name="ccc")


        # Timing constraint
        for i in range(self.number_job):
            if len(self.job_predecessors[i]) !=0:
                for j in self.job_predecessors[i]:
                    sum_ti=0
                    sum_tj=0
                    for jm in range(Mo):
                        for t0 in range(T):
                            sum_ti+=x[i,jm,t0]*t0
                        for t1 in range(T):
                            sum_tj+=x[j-1,jm,t1]*(t1+self.job_model_duration[j][jm+1])
                    m.addConstr(sum_ti>=sum_tj)

        # Resource constraint
        for k in range(self.number_renewable_resources):
            for t3 in range(40):
                use_resource=0
                for j in range(self.number_job):
                    for jm2 in range(Mo):
                        use_resource+=sum(x[j,jm2,tt] for tt in range(max(0,t3-self.job_model_duration[j+1][jm2+1]),t3))*self.job_model_resource[j+1][jm2+1][k]
                m.addConstr(self.resource_capacity[k]-use_resource>=0)

        for r in range(2):
            use_unresource=0
            for j in range(self.number_job):
                for t4 in range(T):
                    use_unresource+=sum(x[j,mm,t4]*self.job_model_resource[j+1][mm+1][2+r] for mm in range(Mo))
            m.addConstr(self.resource_capacity[r+2]-use_unresource >=0)

        m.setParam("TimeLimit", 1800)
        m.write('./outfile/PSMO_lnear_model.lp')
        m.optimize()


        # Get the solution
        doc = open("./outfile/best_solution.txt", "w")
        start=[]
        model=[]
        count=0
        order_dict={}
        for v in m.getVars():
            if v.x!=0 :
                if count<=15:
                    print('%s %g' % (v.varName, v.x),file=doc)
                    a=eval(v.varName[1:])
                    model.append(a[1]+1)
                    start.append(a[2])
                    count += 1
                else:
                    print(v.varName,v.x,file=doc)
                    f=int(v.varName[5])
                    t=int(v.varName[-3:-1])
                    order_dict[f,t]=v.x
                    count+=1
        finish=[]
        count=0
        for start1 in start:
            finish.append(start1+self.job_model_duration[count+1][model[count]])
            count+=1

        # print('Obj: %g' % m.objVal)
        print('model',model,file=doc)
        print('start',start,file=doc)
        print("finish",finish,file=doc)


        un=[]
        for re in range(self.number_unrenewable_resources):
            un1_list = []
            for i in range(self.number_job):
                un1_list.append(self.job_model_resource[i+1][model[i]][re+2])
            un.append(copy.copy(un1_list))
        for k in range(len(un)):
            print("活动资源%s需求："%k,un[k],file=doc)


        Ift = [[round(0,2) for _ in range(T)] for re in range(self.number_unrenewable_resources)]
        for re in range(self.number_unrenewable_resources):
            for t in range(10, T - 10):  # 项目开始前的预留时间10天
                use_unrenew = 0
                for job in range(1, self.number_job - 1):
                    if start[job] < t <= finish[job]:
                        use_unrenew += (self.job_model_resource[job + 1][model[job]][re + 2]) / self.job_model_duration[job + 1][model[job]]
                L = 0
                if (re,t-L) in order_dict.keys():
                    Ift[re][t] = Ift[re][t - 1] + round(order_dict[re,t-L],2) - round(use_unrenew,2)
                else:Ift[re][t] = Ift[re][t - 1] - round(use_unrenew,2)
            Ift[re]=[round(Ift[re][i],2)for i in range(len(Ift[re]))]

        for i in range(self.number_unrenewable_resources):
            print("资源%s库存变化"%i,Ift[i],file=doc)
            plt.plot(Ift[i])


            plt.xlabel("项目周期（天）")
            plt.ylabel("库存数量（件）")
            plt.yticks([2, 4, 6, 8, 10, 12])
            plt.xticks([3 * i for i in range(T // 3)])
            plt.savefig("./outfile/inven_res"+str(i)+".png")
            plt.show()
        doc.close()
        return start,finish