from sympy import *
import sys
import os


def extract_var(file_ptr):
##    Extracts the no. of variables (num), list of variables (var_list)
##    and their states (state_list)
##    state_list is -1 if not state variable, else is the index of the variable

    while True:
        line = file_ptr.readline()
        if not line:
            print "Invalid file input"
            sys.exit()
        if "Variables" in line:
            break

    num = int(line.strip("Variables ()\r\n"))
    line = file_ptr.readline()
    var_list = []
    var_to_remove = []  ## for $DER
    losspower_idx = []
    state_list = []


    for i in range(num):
            line = file_ptr.readline()

            if "STATE" in line:
                state_list.append(i)
            else:
                state_list.append(-1)

            line = line.replace(line[0:line.find(":")+1],"")
            line = line.replace(line[line.find(":"):],"")
            line = line.replace("output","")    #.replace(".signalSource.y","")
            line = line.replace("$DER.","")
            line = line.strip()
            if line not in var_list:# and
                var_list.append(line)
            if "LossPower" in line:
                var_to_remove.append(i)

    return num, var_list, var_to_remove, state_list





def extract_var_inout(file_ptr, var_list):
##  Extracts the output variable
    file_ptr.seek(0)
    while True:
        line = file_ptr.readline()
        if "offset" in line:
            break
    line = line.replace("offset\";","")
    in_type = line[line.rfind("\"")+1:].strip()
    line = line[:line.find(".offset")]
    in_var_def = line[line.rfind(" "):].strip()

    in_var = in_var_def + ".signalSource.y"

    if in_type == "Voltage":
        out_var_def = ""
        for i in range(len(var_list)):
            if in_var_def in var_list[i] and var_list[i].endswith("i"):
                out_var_def = var_list[i]

        if out_var_def == "":
            while True:
                line = file_ptr.readline()
                if "AliasVariables" in line:
                    break
            num = int(line.strip("AliasVariables:\r\n"))
            while True:
                line = file_ptr.readline()
                if in_var_def + ".i" in line:
                    break
            out_var_def = line[line.find("=")+1:line.find(".ckt")].strip()

    if in_type == "Current" and in_var not in var_list:
        for i in range(len(var_list)):
            if in_var_def in var_list[i] and var_list[i].endswith("v"):
                out_var_def = var_list[i]

        while True:
            line = file_ptr.readline()
            if "AliasVariables" in line:
                break
        ##num = int(line.strip("AliasVariables:\r\n"))
        while True:
            line = file_ptr.readline()
            if "output" in line:
                break

        line = line[line.find("=")+1: line.find(".ckt")-1].strip().strip("-")
        in_var =  line

    # do not delete these two prints
    print "Choose the output variable: (type the number combinations):"
    print "Default output variable: ", out_var_def

    index = 0
    out_var_list = []
    for i in range(len(var_list)):
        if "LossPower" not in var_list[i] and in_var != var_list[i] and\
        ".p.v" not in var_list[i] and ".n.v" not in var_list[i]:
            out_var_list.append(var_list[i])
            print index+1, ":", var_list[i], ",\t", # do not delete this print
            index += 1


    out = raw_input().strip()
    if out == "":
        out_var = out_var_def
    else:
        out = out.replace("-"," - ").replace("+"," + ")
        out = out.split()

        for i in range(len(out)):
            if out[i] != "-" and out[i] != "+":
                out_var_index = int(out[i])
                out[i] = out_var_list[out_var_index -1]

        out_var = ""
        for i in range(len(out)):
            out_var = out_var + str(out[i]) + " "
        out_var = out_var.strip()

    print "Output: ", out_var, "\n"   # do not delete this print

    return in_var, out_var




def extract_eqn(file_ptr, num, var_list, var_out):
##    Extracts the equations and returns list of the equations (eqn_list)

    file_ptr.seek(0)
    while True:
        line = file_ptr.readline()
        if "Equations" in line:
            break

    line = file_ptr.readline()
    eqn_list = []
    eqn_to_remove = [] ## for Dummy Der eqn, LossPower eqns
    newvar_index = [] ## for a new output combination

    for i in range(num):
        line = file_ptr.readline()
        line = line.replace(line[0:line.find(":")+1],"")

        if "LossPower" in line or "signalSource.startTime" in line:
            eqn_to_remove.append(i)
            eqn_list.append(line.replace(" ","").strip())
            continue

        if "$DER" in line:
            temp = line.split()
            for j in range(len(temp)):
                if "$DER" in temp[j]:
                    temp[j] = temp[j].replace("$DER.","der(") + ")"

            line = "".join(temp)

            line = line.replace("="," = ").replace("+"," + ").replace("-"," - ")

            temp = line.split()
            for j in range(len(temp)):
                if "=" not in temp[j] and "+" not in temp[j] and "-" not in temp[j]:
                    if "der" in temp[j] or temp[j] == "0.0":
                        chk = 1
                    else:
                        chk = 0
                        break
            if chk == 1:
                line = "".join(temp).replace("der(","").replace(")","")

            if line not in eqn_list:
                eqn_list.append(line.replace(" ","").strip())
            else:
                eqn_to_remove.append(i)
        else:
            eqn_list.append(line.replace(" ","").strip())

    ## add a separate new equation for combined output variables
    ## else, return eqn_list and eqn_to_remove
    if var_out not in var_list:
        var_out = var_out.split()
        eqn_temp = []

        for j in range(len(var_out)):
            for i in range(len(eqn_list)):
                if var_out[j] != "-" and var_out[j] != "+" and \
                "der" not in eqn_list[i]:
                    if var_out[j] + "=" in eqn_list[i] or \
                    "-" + var_out[j] + "=" in eqn_list[i]:
                        eqn_temp.append(eqn_list[i])
                        break
                    if "=" + var_out[j] in eqn_list[i] or\
                    "=-" + var_out[j] in eqn_list[i]:
                        temp = eqn_list[i].partition("=")
                        eqn_temp.append(temp[2] + "=" + temp[0])
                        break


        for i in range(len(eqn_temp)):
            if eqn_temp[i].startswith("-"):
                eqn_temp[i] = eqn_temp[i][1:].replace("=","=-(") + ")"


        eqn_new_r = ""

        j = 0
        for i in range(len(var_out)):
            if var_out[i] == "-" or var_out[i] == "+":
                eqn_new_r = eqn_new_r + var_out[i]
            else:
                eqn_temp[j] = eqn_temp[j].partition("=")
                eqn_new_r = eqn_new_r + eqn_temp[j][2]
                j += 1

        eqn_new_r = str(simplify(eqn_new_r.replace(".","_"))).replace("_",".")

        eqn_new =  "out_eqn=" + eqn_new_r

        eqn_list.append(eqn_new)

        eqn_r_split = eqn_new_r.split()

        eqn_new_var = []
        for i in range(len(eqn_r_split)):
            if eqn_r_split[i] != "+" and eqn_r_split[i] != "-":
                eqn_new_var.append(eqn_r_split[i])

        for i in range(len(var_list)):
            for j in range(len(eqn_new_var)):
                if var_list[i] in eqn_new_var[j]:
                    newvar_index.append(i)

        var_list.append("out_var")

    return eqn_list, var_list, newvar_index, eqn_to_remove




def eqnvar_index(file_ptr, newvar_index, var_to_remove, eqn_to_remove):
##    Extracts the transpose incidence matrix (tr_inc_mat) and returns it
##    tr_inc_mat rows=variable index, each row element=equation no.
    file_ptr.seek(0)
    while True:
        line = file_ptr.readline()
        if "Transpose Incidence Matrix (row == var)" in line:
            break
    line = file_ptr.readline()
    line = file_ptr.readline()
    num = int(line[line.find(":")+1:])

    eqn_index = []
    for i in range(num):
        line = file_ptr.readline()
        var_num = int(line[0:line.find(":")]) - 1
        line = line.replace("-","")
        line = line.replace(line[0:line.find(":")+1],"")
        line = line.split()

        for j in range(len(eqn_to_remove)):
            if str(eqn_to_remove[j]+1) in line:
                line.remove(str(eqn_to_remove[j]+1))

        for j in range(len(line)):
            line[j] = int(line[j])-1

        eqn_index.append(line)


    if newvar_index != []:
        eqn_index.append([num])
        for i in range(len(newvar_index)):
            eqn_index[newvar_index[i]].append(num)

    return eqn_index





def reorder_var_eqn(eqn_list, eqn_to_remove, var_list, var_to_remove,\
                    state_list, var_in, var_out, eqn_index):
##    Reorders the variable and equations according to R, M
##    and returns r_len, var_list_new, mat_new

    num = len(var_list)
    num_state = num

    if var_out not in var_list:
        var_out = var_list[-1]
        num_state = num - 1

    var_list_final = []
    var_index = []
    eqn_list_final = []

    for i in range(num_state):
        if state_list[i] != -1:
            var_list_final.append(var_list[i])
            var_index.append(i)

    var_list_final.append(var_in)
    var_index.append(var_list.index(var_in))
    var_list_final.append(var_out)
    var_index.append(var_list.index(var_out))

    for i in range(num):
        if var_list[i] not in var_list_final and "LossPower" not in var_list[i]:
            var_list_final.append(var_list[i])
            var_index.append(i)

    eqn_list_index = []
    for i in range(len(eqn_list)):
        for j in range(len(var_index)):
            eqn_index_temp = eqn_index[var_index[j]]
            for k in range(len(eqn_index_temp)):
                if eqn_index_temp[k] not in eqn_list_index:
                    eqn_list_index.append(eqn_index_temp[k])

    for i in range(len(eqn_list_index)):
        eqn_list_final.append(eqn_list[eqn_list_index[i]])

    eqn_index_final = [[]]

    for i in range(len(eqn_list_final)):
        k = 0
        for j in range(len(var_list_final)):
            if var_list_final[j] in eqn_list_final[i]:
                if i == 0:
                    eqn_index_final[i].append(j)
                elif k == 0:
                    eqn_index_final.append([])
                    eqn_index_final[i].append(j)
                    k = k + 1
                else:
                    eqn_index_final[i].append(j)

    for i in range(len(eqn_list_final)):
        eqn_list_final[i] = eqn_list_final[i].replace("0.0","0").replace(".","_")
        eqn_list_final[i] = eqn_list_final[i].replace("der","s*")

    eqn_list_final = eqn_lhs(eqn_list_final)

    for i in range(len(var_list_final)):
        var_list_final[i] = var_list_final[i].replace(".","_")

    return var_list_final, eqn_list_final, eqn_index_final



def eqn_lhs(eqn_list):
    for i in range(len(eqn_list)):
        eqn = eqn_list[i].partition("=")
        eqnl = simplify(eqn[0])
        eqnr = simplify(eqn[2])
        eqn_list[i] = str(eqnl - eqnr).replace("+ ","+").replace("- ","-")

    return eqn_list




def poly_matrix(eqn_list, var_list, eqn_index):
##    poly_matrix(eqn,len(var_new),var_new,inci_index)
##    Creates the polynomial matrix (mat) and returns it
    num_var = len(var_list)
    num_eqn = len(eqn_list)
    polymat = Matrix(zeros(num_eqn,num_var))
    const = []

    for i in range(num_eqn):
        eqn = eqn_list[i].split()
        for j in range(len(eqn_index[i])):
            v_idx = int(eqn_index[i][j])
            v = var_list[v_idx]

            for k in range(len(eqn)):
                if v in eqn[k]:
                    eqn[k] = eqn[k].replace(v,'1')
                    eqn[k] = simplify(eqn[k].replace("_actual",""))
                    polymat[i,v_idx] = eqn[k]
                    eqn[k] = simplify(str(eqn[k]).lstrip("-").rstrip("*s"))
                    if eqn[k] != 1 and eqn[k] not in const:
                        const.append(eqn[k])

    return polymat, const



def output(out_files, out_data, arg_out_path):
    #output_data =0.num_state,1.num_invar,2.num_outvar,3.var_list,4.polymat,5.const

    try:
        os.mkdir(arg_out_path)
    except:
        pass
    os.chdir(arg_out_path)

    num_state = out_data[0]
    num_invar = out_data[1]
    num_outvar = out_data[2]
    var_list = out_data[3]
    polymat = out_data[4]
    const = out_data[5]

    var_len = len(var_list)
    row = polymat.shape[0]
    col = polymat.shape[1]

    var = out_files[0]
    eqn_sce = out_files[2]

    f_out_var = open(var,'w')
    for i in range(var_len):
        f_out_var.write(str(i+1) + "." + str(var_list[i]) + ",  ")

    f_out_var.close()


    f_out_sce = open(eqn_sce,'w')
    for i in range(len(const)):
        f_out_sce.write(str(const[i]) + " = 1;\n")

    f_out_sce.write("num_state = " + str(num_state) + ";\n")
    f_out_sce.write("num_invar = " + str(num_invar) + ";\n")
    f_out_sce.write("num_outvar = " + str(num_outvar) + ";\n")
    f_out_sce.write("s = poly(0,'s'); \npolymat = ...\n[")

    for i in range(row):
        f_out_sce.write(str(polymat[i,:]))
        if i < row-1:
            f_out_sce.write(";\n")
        else:
            f_out_sce.write(" ];\n")

    f_out_sce.close()


    if "win32" in sys.platform:
        print "\nOutput files are stored in the path " + os.getcwd() + "\\" + "\n\n"
    elif "linux" in sys.platform:
        print "\nOutput files are stored in the path " + os.getcwd() + "/" + "\n\n"

