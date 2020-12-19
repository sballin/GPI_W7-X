% MLP_Bias = [20 200 400 600 800 1000 3000 5000 15884 15384 14583 13384 13884];
% MLP_LB = [16150 16287 55 214 363 519 2078 3612 15745 15368 14590 13822 14208];
% MLP_PC = [1026 16190 14279 11394 5729 0 11254 15462 3021 3841 4298 4318 4323];
% 
% PCR_Bias = [16249 19 299 375 547 726 2479 4231 15798 15359 14488 13604 14045];
% PCR_PC = [1211 16182 14012 10818 6292 0 10559 15337 3460 4360 4889 4908 4908];



MLP_Bias = [16184 200 16284 15384];
MLP_LB = [15984 16285 16055 15366];
MLP_PC = [152 16100 880 2007];

PCR_Bias = [16065 20 16145 15355];
PCR_PC = [1283 16042 1005 2294];











for i=1:length(MLP_Bias)
if MLP_Bias(i)>8191
    MLP_Bias(i) = MLP_Bias(i)-8191*2;
end

if MLP_LB(i)>8191
    MLP_LB(i) = MLP_LB(i)-8191*2;
end

if MLP_PC(i)>8191
    MLP_PC(i) = MLP_PC(i)-8191*2;
end

if PCR_Bias(i)>8191
    PCR_Bias(i) = PCR_Bias(i)-8191*2;
end

if PCR_PC(i)>8191
    PCR_PC(i) = PCR_PC(i)-8191*2;
end

end

figure(1)
hold on
plot(PCR_Bias,PCR_PC,'*')
xlabel('PCR Bias')
ylabel('PCR PC')
hold off

figure(2)
hold on
plot(MLP_Bias,PCR_Bias,'*')
xlabel('MLP Bias')
ylabel('PCR Bias')
hold off

figure(3)
hold on
plot(PCR_Bias,MLP_LB,'*')
xlabel('PCR Bias')
ylabel('MLP LB')
hold off

figure(4)
hold on
plot(PCR_PC,MLP_PC,'*')
xlabel('PCR PC')
ylabel('MLP PC')











