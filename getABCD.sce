//uCol = num_state + num_invar; 
//yCol = uCol + num_outvar;

// using new functions ReOrderStateEqns
// it brings all the state eqn to top
polymat = ReOrderStateEqns(polymat, num_state);

Rcols = [1:(num_state + num_invar + num_outvar)];
Mcols = [(num_state + num_invar + num_outvar + 1) :size(polymat,'c')];

//Mcols = filt(1:size(polymat,'c'), Rcols);
// row elimination
//eqn_to_remove = findRow(coeff(polymat,0), num_state+1);
//EqnsToKeepInPolymat = [1:eqn_to_remove-1, eqn_to_remove+1:size(polymat,'r')];
//Rmin = polymat(EqnsToKeepInPolymat,:);
//Rmin = MinKer(Rmin);

Rmin = MinKer(polymat);


R = Rmin(:, Rcols);
M = Rmin(:, Mcols);

//disp(max(degree(M)),'to check if 0');

M = coeff(M,0);

LeftAnnihilator = kernel(M')';
LeftAnnihilator = IpolishLeftAnn(LeftAnnihilator,num_state);

Rker1 = LeftAnnihilator*R;
premultIdown = gauss(coeff(Rker1(:,$), 0));
Rker2 = premultIdown*Rker1;

[Rker2,A,B,C,D] = RowManipulatePlusIs(Rker2, num_state);
