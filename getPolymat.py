import sys
import os
from sympy import *
import getPolyMatFunctions as gpf


def main():
    if len(sys.argv)==1:
        print "Enter the input file name!"
        sys.exit()
    arg_in = str(sys.argv[1])

    try:
        f_in = open(arg_in,'r')
    except:
        print "Filename \"" + arg_in + "\" does not exist!"
        sys.exit()

    arg_in_file = arg_in[arg_in.rfind("\\")+1:].replace(".txt","")
    ##arg_in_path = arg_in[0:arg_in.rfind("\\")+1]
    arg_in_path = os.getcwd()


    arg_out_var = arg_in_file + "_var.txt"
    arg_out_eqn_txt = arg_in_file + "_eqn.txt"
    arg_out_eqn_sce = arg_in_file + "_eqn.sce"

    output_files = arg_out_var, arg_out_eqn_txt, arg_out_eqn_sce


    if "win32" in sys.platform:
        arg_out_path = arg_in_path + "\\" + arg_in_file + "_output"
    elif "linux" in sys.platform:
        arg_out_path = arg_in_path + "/" + arg_in_file + "_output"


    [var_num, var_list, var_to_remove, state_list] = gpf.extract_var(f_in)

    num_state = 0
    for i in range(len(state_list)):
        if state_list[i] != -1:
            num_state += 1


    [var_in, var_out] = gpf.extract_var_inout(f_in, var_list)

    [eqn_list, var_list, newvar_index, eqn_to_remove] = \
            gpf.extract_eqn(f_in, var_num, var_list, var_out)

    eqn_index = gpf.eqnvar_index(f_in, newvar_index, var_to_remove, eqn_to_remove)

    [var_list_final, eqn_list_final, eqn_index_final] = \
        gpf.reorder_var_eqn(eqn_list, eqn_to_remove, var_list, var_to_remove, \
                            state_list, var_in, var_out, eqn_index)

    [polymat, const] = \
            gpf.poly_matrix(eqn_list_final, var_list_final, eqn_index_final)

    print polymat

    num_invar = num_outvar = 1
    output_data = num_state, num_invar, num_outvar, var_list_final, polymat, const
    gpf.output(output_files, output_data, arg_out_path)









if __name__ == '__main__':
    main()
