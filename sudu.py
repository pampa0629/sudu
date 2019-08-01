# 解法来源： http://www.llang.net/sudoku/skill/1-1.html 
import numpy as np
 
#打印数独当前数值，不确定的用0表示
def show(s):
    out = ""
    for i in range(9):
        for j in range(9):
            out += str(s[i,j])+"  "
            if(j%3==2):
                out += "  "
        print(out)
        out = ""
        if(i%3==2):
            print("")
         
# 格式化list
def str_list(m):
    out = "("
    (indexs,) = np.where(m == 1)
    for i in indexs:
        out += str(i)+","
    out = out.rstrip(',') # 删除最后一个逗号
    out += ")"
    while len(out)<12:
        out = " " + out + " "
    return out

# 格式化数值
def str_value(v):
    out = str(v)
    while len(out)<12:
        out = " " + out + " "
    return out
            
def show_sm(s,m):
    out = ""
    for i in range(9):
        for j in range(9):
            if s[i,j]!=0:
                out += str_value(s[i,j])+" "
                assert(np.sum(m[i,j])==0) # 检查m，必须为空
            else:
                out += str_list(m[i,j])+" "
            if(j%3==2):
                out += "  "
        print(out)
        out = ""
        if(i%3==2):
            print("")
    print("================================================================")
    print("")

# 确定指定位置的值，随之改动关联的各个m值
def ensure_cell(s,m,r,c,v):
    print("row=",r+1,"; column=",c+1,";   value=",v)
    s[r,c] = v
    # 同行 同列 同块中的m均需要去掉 v
    m[r,...,v] = 0
    m[...,c,v] = 0
    b = rc2b(m, r, c, 0)
    b[0:3,0:3,v] = 0
    # r,c 位置m的所有值，必须清空
    m[r,c,...] = 0
    
##########################################################

# 得到数独s中[r,c]位置的maybe值
def maybe_cell(s,r,c):
    values = []
    values.extend(s[r])
    values.extend(s[...,c])
    values.extend(rc2b(s,r,c,1))
    m = [1]*10
    m[0] = 0 # 0位置没用到
    for index in values:
        m[index] = 0
    return m

# 得到元素[r,c]所在block的所有值，rv表示是否把block转为一位数组
def rc2b(s,r,c,rv):
    i = int(r/3)*3
    j = int(c/3)*3
    b = s[i:i+3,j:j+3]
    if rv:
        b = b.ravel()
    return b
    
# 计算数独s对应的可能性结果，返回m
def maybe(s): 
    m = np.zeros((9,9,10), dtype = np.int) 
    for i in range(9):
        for j in range(9):
            if s[i,j]==0:
                m[i,j] = maybe_cell(s,i,j)
    return m

# 规则1：唯余解法：先用maybe得到每个位置的可能值（m）
# 若某个位置的m值只有一个了，则对应的s值就只能是这个m值
def rule1_onlym_cell(s,m):
    change = 0
    for i in range(9):
        for j in range(9):
            (indexs,) = np.nonzero(m[i,j])
            if len(indexs)==1:
                ensure_cell(s,m,i,j,indexs[0])
                change = 1
    if change:
        print("规则1：某个位置只有一个可能的数值，那么就只能是TA了")
        show_sm(s,m)
            
###########################################
            
#找到m中只出现一次的值，返回这个值所在的index列表，没有返回[]
def find_only_m(m):
    values = []
    indexs = []
    (r,c,d) = m.shape
    for k in range(d):
        clip = m[0:r,0:c,k]
        if np.sum(clip)==1:
            values.append(k)
            clip = clip.ravel()
            (nz,) = np.nonzero(clip)
            indexs.extend(nz)
    return (values,indexs)
        
# 规则2：基础摒弃法
# 在某一个行/列/块的m数组中，当某个值只出现一次，那么这个值就只能在该位置
def rule2_onlym_rcb(s,m):
    # 行
    change = 0
    for i in range(9):
        row = m[i:i+1,0:9,...]
        (values,indexs) = find_only_m(row) #从某一行的m中，找到某个值只出现一次的indexs
        for k in range(len(indexs)):
            ensure_cell(s,m,i,indexs[k],values[k])
            change = 1
    if change:
        print("规则2-1：在某一个行的可能数组中，当某个值只出现一次，那么这个值就只能在该位置")
        show_sm(s,m)
    
    # 列
    change = 0
    for j in range(9): 
        column = m[0:9,j:j+1,...]
        (values,indexs) = find_only_m(column) #从某一列的m中，找到某个值只出现一次的indexs
        for k in range(len(indexs)):
            ensure_cell(s,m,indexs[k],j,values[k])
            change = 1
    if change:
        print("规则2-2：在某一个列的可能数组中，当某个值只出现一次，那么这个值就只能在该位置")
        show_sm(s,m)

    # 块        
    change = 0
    for i in range(3): 
        for j in range(3): 
            block = m[i*3:i*3+3,j*3:j*3+3,...]
            (values,indexs) = find_only_m(block) #从某一块的m中，找到某个值只出现一次的indexs
            for k in range(len(indexs)):
                r = i*3 + int(indexs[k]/3)
                c = j*3 + indexs[k]%3
                ensure_cell(s,m,r,c,values[k])
                change = 1
    if change:
        print("规则2-3：在某一个块的可能数组中，当某个值只出现一次，那么这个值就只能在该位置")
        show_sm(s,m)
    
###############################################################################
    
# 规则3：区块摒弃法： 
# 当某block中，仅仅在一行/一列中有某个m值，则同行/同列中，不能再有该m值
# 当某行/列中，仅仅在一个block有某个m值，则该block的其它行/列，不能再有该m值
# (1,x) (1,y) -->      (1,x) (1,y)  : 1 只能在该行的第一块中
# (x,y) (x,y)          (1,x) (1,y)       
def rule3_onlym_block(s,m):
    # 块
    change = 0
    for i in range(3):
        for j in range(3):
            r = i*3 # 起始行
            c = j*3 # 起始列 
            for v in range(1,10):
                # 得到这个block数值为v的所有index，判断是否属于同一个行/列
                (rs,cs) = np.where(m[r:r+3,c:c+3,v] == 1)
                if len(rs) == 2 or len(rs) == 3: # 2-3个才需要判断是否在同一行/列
                    uni_rs = np.unique(rs)
                    if len(uni_rs)==1: # 就一个值，说明是同一行
                        m_copy = m.copy()
                        m[uni_rs[0]+r,0:c,v] == 0
                        m[uni_rs[0]+r,c+3:9,v] == 0
                        if np.array_equal(m,m_copy)==0:
                            print("row=",uni_rs[0]+r+1,"; b_column=",c+1,"; value=",v)
                            change = 1
                    uni_cs = np.unique(cs)
                    if len(uni_cs)==1: # 就一个值，说明是同一行
                        m_copy = m.copy()
                        m[0:r,uni_cs[0]+c,v] == 0
                        m[r+3:9,uni_cs[0]+c,v] == 0
                        if np.array_equal(m,m_copy)==0:
                            print("b_row=",r+1,"; column=",uni_cs[0]+c+1,"; value=",v)
                            change = 1
    if change:
        print("规则3-1：当某block中，只在一行/一列中有某个m值，则同行/同列中，不能再有该m值")
        show_sm(s,m)

    # 行： 
    change = 0
    for i in range(9):
        for v in range(1,10):
            # 得到i行中，值为v的所有m的indexs（全局）
            (indexs,) = np.where(m[i,...,v] ==  1) 
            if len(indexs) == 2 or len(indexs) == 3: # 2-3个才需要判断是否在同一块
                bi = np.divide(indexs,3) # 块序号
                uni_bi = np.unique(bi)   # 都一样
                if len(uni_bi) == 1:
                    print("i=",i,"; indexs=",indexs)
                    k = uni_bi[0]*3 
                    rs = range(int(i/3)*3,int(i/3)*3+3) # 得到关联的三行
                    for ii in rs:
                        if ii != i: # 不同行才修改
                            print("row=",i+1,"; value=",v)
                            m[ii,k:k+3,v] == 0
                            change = 1
    if change:
        print("规则3-2：某一行中，仅仅其中一块有m值，则该块的其它行不能再有该值")
        show_sm(s,m)
    
    # 列： 
    change = 0
    for j in range(9):
        for v in range(1,10):
            # 得到i行中，值为v的所有m的indexs（全局）
            (indexs,) = np.where(m[...,j,v] ==  1) 
            if len(indexs) == 1: # 只有一个时，换方法
                pass 
            if len(indexs) == 2 or len(indexs) == 3: # 2-3个才需要判断是否在同一块
                bi = np.divide(indexs,3)
                uni_bi = np.unique(bi)
                if len(uni_bi) == 1:
                    k = uni_bi[0]*3 
                    rs = range(int(j/3)*3,int(j/3)*3+3)
                    for jj in rs:
                        if jj != j:
                            print("column=",j+1,"; value=",v)
                            m[k:k+3,jj,v] == 0
                            change = 1
    if change:
        print("规则3-3：某一列中，仅仅其中一块有m值，则该块的其它列不能再有该值")
        show_sm(s,m)
    
#########################################################

# 假设法，
def ruleN_define(s,m):
    print("规则N：假设暴力破解法")
    for i in range(9):
        for j in range(9):
            copy_s = s.copy()
            copy_m = m.copy()
        
            (vs,) = np.where(m[i,j]==1)
            if len(vs) == 2:
                for v in vs:
                    print("假设：row=",i+1,"; column=",j+1, "; value=",v)
                    ensure_cell(s,m,i,j,v)
                    for n in range(5):
                        print("开始进行五遍普通规则的尝试，这是第%d遍"%(n+1))
                        rules(s,m)
                        if check(s): # 确定OK了
                            print("搞定了，正确结果如下：")
                            show(s)
                            np.savetxt("out.txt",s,fmt='%2d', delimiter=',')
                            return 
                        elif isFailed(s,m): # 失败了就要把v去掉
                            print("假设失败，删除m中可选项；")
                            print("row=",i+1,"; column=",j+1, "; value=",v)
                            copy_m[i,j,v] = 0
                            break
                    print("尝试五遍后没有得到结果，回退")
                    s = copy_s.copy()
                    m = copy_m.copy()
                    show_sm(s,m)
                    
    
# 组合各个规则判断
def rules(s,m):
    rule1_onlym_cell(s,m)
    rule2_onlym_rcb(s,m)
    rule3_onlym_block(s,m)
    
#########################################
    
# 判断是否已经出问题，不能继续了
# 出问题返回1，没发现问题返回0
def isFailed(s,m):
    for i in range(9):
        for j in range(9):
            if s[i,j] == 0 and np.sum(m[i,j])==0:
                print("发现错误：row=",i+1,"; column=",j+1)
                return 1
    return 0
    
# 判断是否ok了，搞定了返回 1
def check(s):
    m = maybe(s)
    # 检查 m 都必须为空
    if np.sum(m) > 0:
        return 0
    # 检查 s 每个位置上都有数字
    for i in range(9):
        for j in range(9):
            if s[i,j] == 0:
                return 0
    # 检查每一行/列都不得有重复数字
    for i in range(9):
        uni_r = np.unique(s[i])
        uni_c = np.unique(s[...,i])
        if len(uni_r) != 9 or len(uni_c) != 9:
            return 0
    return 1

# 总入口
def sudo(s):
    m = maybe(s)
    show_sm(s,m)
    
    for i in range(5):
        if check(s)==0:
            rules(s,m)
    if check(s)==0:
        ruleN_define(s,m)

###########################################################
    
s = np.loadtxt("input.txt",dtype=int, delimiter=',')
show(s)
sudo(s)
