
for f in range(F):
    for s in range(S):
        for t in range(T):
            m.addConstr(sum(y[f ,k ,s ,t] for k in range(K) )< =1 ,name="ccc2")

            if Qfst[f, s, t] >= 1:
                if Qfst[f, s, t] <= 5:
                    obj31 += (self.Ofs[s][f] + self.CNfks[s][f][0] * Qfst[f, s, t])  # *y[f,k,s,t]
                elif Qfst[f, s, t] <= 10:
                    obj31 += (self.Ofs[s][f] + self.CNfks[s][f][1] * Qfst[f, s, t])  # *y[f,k,s,t]
                elif Qfst[f, s, t] >= 10:
                    obj31 += (self.Ofs[s][f] + self.CNfks[s][f][1] * Qfst[f, s, t])
