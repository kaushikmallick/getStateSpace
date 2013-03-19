// ReOrderStateEqns > findRow > filt
// MinKer > polyRank
// IpolishLeftAnn > rowcmprI
// gauss > RowManipulatePlusIs


// function that takes first input a vector v1 of indices (assumed distinct integers),
// and second input v2 of what is required from within v1.
// and gives two outputs: one is v1 with just v2, and second is v1 without v2 =: v3
// v2 is possibly two elements, but v1 will always have v2 as it is

function [filteredOut, filteredIn] = filt(v1, v2)
	filteredIn = v2;
	lV2 = length(v2)
	filteredOut = v1
	// v2 = -gsort(-v2)
	for i = 1:lV2,
		filteredOutIndx = find(filteredOut ~= v2(i))
		filteredOut = filteredOut(filteredOutIndx)
	end
endfunction




// function that takes a matrix and a col-index and returns 
// a row index that has a one in exactly
// that col-index in that row (if such a row exists).
// assume there is just one row like this, or else first such row, if none
// such row exists, then rowIndx = 0!

function rowIndx = findRow(A,colIndx)
	allNZrows = find(abs(A(:,colIndx)) >= 0.001)
	for i = allNZrows,
		if norm(A(i, filt(1:size(A,'r'), colIndx))) <= 0.001 then
			rowIndx = i
		else
			rowIndx = 0
		end
	end
endfunction




// function that takes a polynomial matrix and also the number_of_states
// and re-orders the rows for as many times as the states

function PmatOut = ReOrderStateEqns(PmatIn,num_states)
	for i = 1:num_states,
		rowIndx = findRow(degree(PmatIn),i);
		NRows = size(PmatIn,'r');
		NewRows = [1:i-1, rowIndx, i:rowIndx-1, rowIndx+1:NRows];
		PmatIn = PmatIn(NewRows,:);
	end
	PmatOut = PmatIn
endfunction




// a function that takes a polynomial matrix and
// evaluates it at several random complex numbers and returns back
// the maximum of all the ranks (of each of these complex matrices)
// as the "normal rank".

function rk = polyRank(R)
	count = 40
	rk = 0;
	a = 3*(rand(1,count) + %i*rand(1,count) -0.5 -0.5*%i)
	for i = a,
		rk = max(rk, rank(horner(R,i), 0.0001));
	end
endfunction



// a function that takes a polynomial matrix and goes on taking its rows : row by row.
// It skips a row when rank is not increasing

function Rmin = MinKer(R)
	rows = size(R, 'r')
	cols = size(R, 'c')

	Rmin = R(1,:)
	rk = polyRank(Rmin)
	for i = 2:rows,
		if polyRank([Rmin; R(i,:)]) > rk then
			Rmin = [Rmin; R(i,:)]
			rk = rk + 1
		// else   disp(i)
		end 
	end
endfunction



// function that takes a *tall* matrix (assumed full column rank0 and gives 
// two square (expected to be nonsingular) matrices that bring E to be 
// not just row compressed, but I matrix, either up (first output) or down (second output)

function premultIup = rowcmprI(E)
	LeftInverse = pinv(E)
	LeftAnnihilator = kernel(E')'
	premultIup = [LeftInverse; LeftAnnihilator]
	premultIdown = eye(premultIup);
endfunction



// function that takes a left annihilator and modifies that annihilator
// to get the left-most block as [I;0] so that state-derivative-s does
// not mess up with lower equations!
// this function *assumes* the first few rows/colummns are ddt x part.

function LeftAnnihilOut = IpolishLeftAnn(LeftAnnihilIn,num_states)
	if rank(LeftAnnihilIn(:, 1:num_states), 0.0001)==num_states then // f.c.r. check
		premultIup = rowcmprI(LeftAnnihilIn(:, 1:num_states))
		LeftAnnihilOut = premultIup*LeftAnnihilIn
	else 
		disp("sorry, Left Annihilator not polished/modified!")
		LeftAnnihilOut = eye(size(LeftAnnihilIn,'r'),size(LeftAnnihilIn,'r'))
	end
endfunction



// function that gives a Gauss transform to *lower* triangularize! (for getting 
// y variables out of state evolution equations)

function premultIdown = gauss(vect)
    premultIdown = eye(length(vect), length(vect))
    premultIdown(:,$) = -vect(:,$)/vect($,$)
    premultIdown($,$) = 1/vect($,$)
endfunction




// function to get sI-A, rather than some other I (with some diagonals  as -1) multiplying
// to the s. this function takes kernel representation and number of states 
// and multiplies entire row by -1 if necessary. Then A,B,C,D are extracted out.

function [Rker2, A, B, C, D] = RowManipulatePlusIs(Rker, num_states)
	rows = size(Rker,'r')

    	for i = 1:rows,
        	if degree(Rker(i,i)) == 1 then
            		Rker2(i,:) = Rker(i,:)/abs(coeff(Rker(i,i),1))
            		if abs(coeff(Rker(i,i),1)+1) <= 0.001 then
                		Rker2(i,:) = -Rker(i,:)
            		end
        	else
            		Rker2(i,:) = Rker(i,:)
        	end
    	end

	// Rker2 = Rker
	// for i = 1:num_states,
	//	if abs(coeff(Rker(i,i),1)+1) <= 0.001 then
	//		Rker2(i,:) = -Rker(i,:)
	//	end
	// end
	
	A = -coeff(Rker2(1:num_states, 1:num_states), 0)
	B = -coeff(Rker2(1:num_states, num_states+1), 0)
	C = -coeff(Rker2(num_states+1, 1:num_states), 0)
	D = -coeff(Rker2(num_states+1, num_states+1), 0)

	if D < 0 then
		C = -C;
		D = -D;
	end
endfunction

