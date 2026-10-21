import hashlib
import json
import sys
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
INV5 = pow(5, -1, P - 1)
MASK256 = (1 << 256) - 1
# Round constants of the deployed Orchard parameter set (zcash/halo2 halo2_poseidon
# 0.2.0, P128Pow5T3: 64 rounds x 3 lanes), as base-36 field elements.
# Round constants of the deployed Orchard parameter set, as base-36 field elements
RC = [[int(x, 36) for x in line.split()] for line in """\
1chz1m499qw57k1bmqtj3p11pgvlbnugrv8jo7ce2xpfuh0emb 136lyldts0l2odfnn4ucu51kvpxljsb4obmkp22gasnf83r8uj ivwzu26na04s8mkyloof8yunj5cptktrv9pl6qg8m6epi9cjs
199931vzfs5ujcni2a8ml47yn16ecg43d00y2e9mg825tppub6 6i2flekwhzvkmzongc39wiwfx1uuho9ap7tr710z8rhlcjhkj 11v3191rrrabl0cl0t5od8b1yqflq0m4gfv3kj9ymw8p3aq2fs
z05hkf43v0gvrcd0gnmh6aa9b19cr1jnus2d7182o6vi5xgh9 zosc845eiyjuax07zbrmqefw4iacn9gt53qq34ch1fxxpa4j8 p0drdo67tdx9z65a8qtk92cabo3392uh5xo5mtkd6vm7u48vt
jvxuyoh0jqdohcm8pnirdejbso68ju7trhreodbd4yqxyluy2 14gqxmeljvegvafrgfrwmiei2a6qxltmo0kfu9qiihcwvsjlkc 3uvj2h0uvytr9qgi0f56eijo625h9urv1tmejxmv1epwmlg2c
ps105p0un4kag0d1qevvh60hqp5272aro5h95bae0ilgp9qy7 qc8pzzx5fx6bf6uo3j10b1r771ql1skcgwkh4sx3u5qu2swkl 15tj3bco3iwtzq93bq6nvb0p4jdgob4zu1qr6l47sp6tasbqrz
155yqtf4me7bds9ls5bd6kacu5vpwxj4hpej4ae1jstzy9isgb 15auuzz0ztmckwmsgnxjkpb95p6tsk83y66wa9awqds5c8ex41 dtvzrp2nmivt9w5r3rlwxd30iotm9tht4vw8vvlqkmmiuxj9m
15waaftnbzuokm0sza68uq2ebuhq3739p8v9y3jpj58ivozmfy fku25p9pstfereab10vwp8fpa612wfyfkr4v8l7v897imf5m4 ysym2oei47kuo23tf1cv2yprn8e6hbuhplydu4jv6t5faq2fh
lb1na2f6cw7t5nu6e2h66ybn1ypb9ofvv258iiey4wnmipo7e 1c6p6clbx9e606i9jns07na5lbcvi6rk45p3xb7bwrvo01f0zp 1h0dasjjsfh49u2bjouaz1lop7g7xvzupzihp21u34zg214fj2
146b3qi4i0ev9ktc6ex1l6p7av7vk7sm2qhsthy33bc1u5184t xv3bbcff8vjsoen4hz12orxnhhivq7s5g0twa2qsgvlso7vxi 1faiky5ceyrs8gwc1pv2y0e0fxmdlmr8vpz7wxnoehetf8j0xn
z53gubeqgl1q6t9mf7jnepa32bec3jz5a4ok648eva6qf0sbw 14p2hozrp187gb5ptzs8pv0huh6g17rm1yvaugnl7earb0j5ya k1b3u8g31ahr4ityhu07nn12h4lwa473iwu1e9qwlnao4iiss
oa8yvbib27dpizprk7hm43ctfajev3d7amtd2acg9bt7203q7 dkd3sytu92tptmk6u4p7nlmj52yrz2r27hf7vetdrblfocslk 16cdoilvr4gywc55g6gdw1h5561cira5bj0airtg635k3lmm8w
1gd6jz6yem53xe81qd2qfx55bgxnvvc1fm6kxebnofub3xinzq 1jc04s0t6z57kymyv2gs3itxzldukxrflrt24cwffg80f4ikqq 65kcddje9czl1zsdcoponl19t8amab0weirxu19w6txdc6wo3
5vnhdoejkqmbvge908xotxd96rb5pp5tvo9j002p8yi3qktsj 1cu8zornoktnqhm4ayv98nchsrqxcb6bukye5gtfikytu0nlr3 1fi8w0kt0xg78b58lmmg9db3a73ax105vc2959jjyc9yz6dwa9
tyvxe9pcws3uaq13gfuzbf4zbb1h49n9axvrvg6zs9i7njy0u 1fvfgr47fxiqm3babpt52p0uct028pp61jh5olstwbt7bug4qw sd8vy7keeg3utlmkqp6bpurd1sa3czod7vf7ll626t2coy7cj
27nhb96yf2bwtqxz33hn3pg6vrigfmpwbwi3gus1argik9wvm py7yjffd65i1u1v4x6nkn4czdj7ip2r2jamj37dfnql00w4io gc4owbxjid3pz1xfznufngo6ysagvra0fat69iimrkgbuzk37
krg9b1x2u0pqhrocp22vg6i3wo657s2j8gz6lrotrfrgi0gz8 ku870vbpix4e5si7z97oyekjks0emeyxx2mo8zmo7f5gwqmua 14ngcat9bhaextqkpxeqfu3q6fadfwh51iht9lub1r0pso67pp
j29kk5s9kt45v6s2up3oxhagdmxsq950keg91268p3hy11lu5 b0f18mwxpvfnvdgw3315ngopae6xngzhu6f10845s31tfd2lu 9r98nn6z47bixt98r7wrd8sitjmffdv4pnhll9wsanizqx2x3
18aivji6m78nv3ictcemadp2biow9a7bg9866fuuar7l94xtur ooul7r0ycl6na0sruoj4x9y5wvnq6457s3f332f5ga6ed6s4h 1hxpx0lwhkekfi15agjnqjcen0f1sledmd9aevgl7lt8eyf9cc
hdvp4z8i3fnglpohk543noepw6krqxg0yvmkl78rwcatayika kg1n8yr4qb59wz9hmu7vract6jeqcglv2zy61r9tz5zmjfcgt 105jpfzg7hyruvq7hnmqq4hkz86rglzjyudcem5gu7o6ijithg
b2x3n8knkfaizeki59l35bumq1w3hw44wxk2lvwfc0htekpdy 3d2bdrgo3oqkobxtlpk970uhx2w44qzuvdrhhbbyqqy33wdg5 18g1y9oj2wve60mgiwub9ej90ga8alh5ic5pbk2y2k20lee0yq
kqvu9an8ip5h05b2wm2z99b8dyfm5lle2zk5it2e5hss2e9ga h082d3fcw43q0h8ue16sy0qetw1vmdtj0s23lzlb6ltm65n11 1gbnix6ydk00ajwdiy23juy9pkavvx3uq8yapv3h2a0j5wba0p
f7ftiu5unpuwoolz7a8wndhb3rcfhpv76ml3po39p2pnelm40 8vq784tuhv08inqkx6ttr3u3aesiui53r1zt4v339m710f1g8 1bppczq8sszng4e6yn06bgpzll88f5bm6z46hp5hba9fv6rgtm
4zjdgw4htll62w0c63zb8m2z5ifvpg50sqwh9k6fu1gfpfv8o vkjzltihzqcap3fmg2fdv46lh9mskittum7yya29yecgneepw st63k1v53r1pyoamyat54um1wks84w42s8laty5xy3kbig00j
hgq2wo1thiyiriacktdjb44cevz2nyegvwcuowyywxc27cypo l5hqw2y0q4wt5tmi5z6zyein2i20nmrcg3ci2uodbl31iagfn vabhznhmgl2wli0vspccb361wk8fc96coijm8b405q485eae3
1bmlpxsr3o4w6lrv7wzrf2ciraejdws17d0a1xxq3vajyihjmw 17scv5zwhliuw9ebjkh63emhn701vfeaqo26rwklizysjsixfr xev0stxo4zrivnu378v4ny0g2hwoi597prxgexq08vh78d69y
30f5hpxznr849kaqw46vneelspyzo5zbj37sgnddwo9zya3ke vzy13k9p76ja2lvz5dzcezuhp78a5dfyx8un0n2lsvp82ubgg hmuvg5wb0y9rmwyxzdmv3gd5euahnowj52olapzovcgyuelj6
1g136sl5x46siqelpc79clu4ucv6d3vjhbzt9xnkccc1db5jsp nxsx8knqv3bcz2rewscpfqej6hvie040ckwm6duuzrnonplf1 nqqmlhyyydeoxinqa7qa0hm31vdt5phmpe921yyk8j1j42jwf
zb41xo6q573fnznyhm87c5zqwsj8pxn7lg74n0390dov0r341 15l88lkw1as7rq3lt6ra6z6wzwzbqms05hxq4ofnmgc9kb02h2 i9cw6bg56wlekbgllttrkuloku9vt8l4ikqrva6cdbu7sp1pf
mmysltksilykvkc9xcw9qlma962o4420kf3xern64od4pkkkb 17ll5y7cvkwgq6k6qapg75cyl307nk5v0oleei9dh4l7i4v57w 1dufy3hf5bs4l33amj7z70ut48mfhdssb94rrs17bbgl3rjmr9
15w3z8tpfqhh2nh8rorp2yxyuw22s8klb2jdzlwayiqcesj5vo 1con7ay721lf2yigliv05ujwl3x2vwf6i6rey3ywv44ofg9ghc yqke38eo9jphfr7oortyt8endh8zbfletf7qlavh0fsblpdb2
h1wzlz23srsdfbr3y2fw8wthh5qquqop1sp9x6fydxelnbcet u5yg8lqod3aa525eewvdr1fflyaklv5ez119aee0dxhyzxuts 1ilsfe9nzi812pnbeiygmm5yz3maz5om80el06c7v8xy54ggur
cvk9zgemnvttm05da29o3e9aj4fqv7y24piee5x8xqxldym5l o8xetifskpghdtvyfj07xyhfeigbuaazspsv8d9vciogqzz5p 17ppdnogjapk8awb99tythe3uk0gsx8xlv6i40dw36yl3sjpf0
w7egws2x4p6fand5nzw2xxrxjw0x8naig26yhxspmuegvw553 zins0z8uw7dgn1j1fow3hlw5lw1wxglkmb6dtxz11u6a20rdt 172oyenjxneve62zpd9xs7x4r7lbkpu75ln6wlmp2kmqljayf4
ehvthg3bpugrvn4tw2v5dhsbzz3fg0qhlupxr66qk8pmowao htsk8tddxof3cxq59kja2wuzxozn2uz801t6263hez3gyxneo 3mar9j4qeplv2bg7tt2cmeqgxsxjxir61ndzsbnwqdxi57j51
zfzw6jrki6z2iiaw4uqxxnipw98sxvfojbb9u1e8z664lnpnk 1gcgr4csjrehpg796nvjla4t1r266e1sdazwu70lyn8naq5dgv au4553tk9grcsqjuwunzgq2qv3f3a8laklo44vzvjx2d4nr1w
it0nmzmvwimsj9oz75wlvz9j02dud5zyr1sdequ1lsj3n17ts 17icvokwrkwyv687l15ivcta8d5iebs8wbr7la3r4pqks3ad32 mrqz3g6wmjj6wxg6ru33r7fsj4t360w00kn0fn9rb761xvdur
vesk8bi1cqw9id0hczt00j29xwnkpfu930rshnj5aofn0f9i5 2c2tvy03ymg1z86szo1cy8rtq9pmhakyexiymqygf9arb1hux 19maab9wkwt5v034nz9km3y77u1n2qfevyv8xp8dnskq8981gg
yhm66nnnmtohoia2ackpy4qgdb1uiu8a1w3itvlm1euintbbz 426edwz3nelgig814zpirq5bfhjmpn50zmzbb8gladgnokkko 60647hfwwygp0f5csc7lqvsii7ldejgfsja0sy5x9tj4db0f6
18k858ea2o0avqf8elwxmwoupbhxmn0p0pnuxc3kg2rdfyncsm vx9tyvzxp6s5lgchc9gcl51vtfncew1xd6zsqczlxvakrg2pv 9bqio4p9zyf7jll6u7z3mzktxj4gb6tlm0orbqjhz2b7q5bdb
uhpklgthi9kfsk9n214dgdtouu2qjsh21xn5f6h7lkaaghgs5 18m1g4c7afo4zu1s49l2d2x7bsmb7ixbbr3d1fxwmyn3fz7tqe 13gzv1lonjzlv8h9jabthl0kdjvhby939p2zne2phi34lq6bu7
gbykco444hotasojjc06wg7557jbynpnt0ihwo6c6spg7urlb zqjme4pe86lwmtse3gnmk6zbdxejxd7uu2lab9yxtwj0ma7ne ymv79q8u8k3qfshlvpnlth8th1zpmwb5uv8ule75hhhzk9cw0
1d5ehd4hbt8bmqa27acb58cbsp43d4otwytr41ymfibwbkqrmd 2fbbfl0mv2vnyixhcxv9lmeylf7f7v2mlifee1vffafd8yp59 a9jst3gpajw4wjrg1ojdd3d3kkpmjnamqtgsm8z3olulpubr9
1l7jnzd4mz8rcfr2vdtzo1em84mwc0iu127q1se0ogih0tr0ue azwf7jb65gti7518zhb95cu1g91w27k31e2n239w69om1g0v3 156u8epu8vdftb8gnvab31meg2ncs7pixpe2x18flyarzupyox
2zotuahruo88kmf01hqabs8wefirhsv1cztds2p98ma69brss a7cgtmufcxpda48kv9jwo4fksmxvpngm0aiq3tnabdiydmldo cperznrol4k7pbfms65n4g7nse3sk0jmoierlozua4lo5gnof
qfx65lkp0qcsj0x4tmqeu9i247rsxr4g8o3t16s0n94nppmhy o30rg19tv6xuc7bmxthkr6t4xp4ysyrik8mcaafn5p38wim19 2887sjlgdhxkl3n0a5los5qo8orm1p7znmlzyofw83em3qa0h
t5swuq66oakcur7io8q3l3pp9colsdan1ismz4p2ge3hfosb7 1j1uhtso6z9xjai05j9bffu4cjzkk9wv8mfe5h2nwp2njyqcne h88aui1ultvzphecsznijb54d7y9q9ofrrs9jy9tkxp55ihl0
y02gceilzsj8ar7l759ywag5d3gxjcuo6e04h2do6siz29evy pdo7p9yzjq7bqq6zxfw10tws9vkaau77w9m8v2gnrk71j8n8p b35u3ajczh89w5u1c4iim9inmnjb0eqqwc6h911tx2191myeb
ev2v4sq1iotj5ba1ofutzhmcurwciqrpzhvqyt0633yogyymn 1ak2rqkatcy9xy1m8hrzof67mfp4n5tx2mzaumy88l6gkjr3hl k1bdminjyjp9kgtcluthjuk5j3ufafucxu8znng4264vhj49f
k5v68831fkwn5e0bplpdv5gj5hah4v3o5dae3vlorb1ique0n 1dstk4pqgmh4zn16xatv98ikm5cs0dzu0sw1hb5df2da4od946 rdod9gxtuled2345mqbd6x9ig4j627dtf6a9m81btcgza4a1q
1btfpbvgnipu9kcwsscgjqsl2sat5f8qxubcncqfp2x3efjr5d px4j413mrwmmj8oit83t0pejhg40xbjmayq8wu0r8plilng3 qd49kmb4q2zfdo58webjuj00hj8hqfeojxm46fcxelv2hl3qk
iajohl4unifvg71tkng1tbzhli1ueb5cw65wg8lwdqs8s0nzr qk5x42smjfb3rg2nw0ydubpused4j506p3vpngkln729adw 1cq6xdb2wv28lcgpx39lxzl0vez0wzq7krfgmfb42vsqt214sk
zel0fsk334phlzxrzgx8iaj6pd4mucchd5mwzcwv6chpp3fu jvzp80yl2yo6zfao3ffep1aqojuy322xu9l5l0o6tcfp1mrnw 11qcotozm23iwsr67s4e21pusge228e0ozrybe8nsl2ii20vx2
8hytfu7fv5yap38bhpdtpb8bjopvlmbeuut42csz9ihn5txoy p00ik8oqnrz5ovtfb5fwltf2xvidomfnb0e1zd8lk0bkvbe5q lvp771cxm1n5u7hvz3popnw9taomlpw89gwxcms94px7hqnhs
s18kxt4c74q9skv37gx55epcf16m83dew4jmgokud50in29n4 o6omi1v32adtkufv15jrold3d8cgm2b3u6l93gpes6p1uyy9y 1ic46mcbgkp3kss3fr5vqe6wqbi4d6mjwf7kjm9yijxf3y7vv9
k2trx0itolqjf4kx1plvaamikc5r98sc0v6ugai30oc69dz7a ducle2mwj6xevqnnhwy3qunpct0flbw295goc11oogskk4onp 2g1piddquq6c5g1hsv7aa7zd819gpy2gmugboo0o3io4r3p6i
iim1wkl7lv2lm0oy8q4ord2gssej0rc1t8fglrz3qjw3w7ohf mg3je7d79pcyuuzo25ekvykfqiadz3wufh2a2w3svq8vqpt16 84049m74dtzadpjxhmnvp031n52l7yeegxfg8r62dqmg0gi53
1enz6dobjl7ufxfbhgnkicxm87fbhfmqgqn1h4jwf1u135jbib 14uvty9g07tmiv64azorz76m8vv6297u9efgkf10tem06z44cm u9duawvg7064vvrzvgdgxatn0kha33vqrjujqt609jsysuhjk
16zd6gwyj74wq2boegfmn6jyp2ms8fqdwux4gqvkccj0y0twuz lyphxtjugyj92s0k5hojvfxz4at37dnqr1vkkplpfynte3a9g a9ift7lakr6n4tnuyxvbgrp1fx07oi9czkjhb6hbmnn31db92
2qni16yvbdr39i7oddi4nyjhls5g47lxtvwxyxdsc9vur33ip 184y6bibqlnaf7thx9160zn4ill5esh4yxfhaghn9ayzm393j9 1a7fr5u945naj6ojl42svdin34bbi8fhjnaobdbwhio8zv04ps
1b71d9uhaxx8urh7x0o3x74frtby3mqtjoyqbyte9qlzqxpno1 28cg8o9t50hkas91t0n9syiojo6wkamjp7wujf9o13urpv3at 3509aio5vqtfhi91hi5deim3hxcx0vj1roxqmqavwm1jy9vxa
s6nj0yh2kq0j36px5c3p8is85s6p2vabp5s2xpzvdyyuxywfi yiwkfmlk6tf0vp9kbe5rrqq4nx68zazkm62ffpo92fe1k9yjt ba1dchef4moadga9xpc7c5vhmo4bvbz7gtauxkgzmz50sawkl
kvoitu2c5baqayd588mpcmns7c2afed0xo8a04tbch7xydud3 119amzzja00wjzx2qpkpmxnc2bmjgbp57i8vp0red6zo7atlpb fibbi13n3t1ymzeica8yo8ue191h8ln0q7g3ez0j4w8bj4rkg
2kz6u3qfkxo1kznv3xibz8rob14pl0bjqw1rk62aj1hxs0f85 bp9ec0hpsp8z1kom8lhrsgz9h83u5m26170hwh4qoemflrl4n hkfed5wa79b3m038bz1v7vijy24gp3i8yr8xzwvpvcckqh108
10sllvnehl45wcsvvrw78xceoxl8uusvhcg0d8djlu4qrzbw6t stpvyz8sne977g4d1l5hti94oljf4dor97m9bz70vofp6a7d3 1gixxd8j9tie2ju784a3klw9eyw9nfzlz99zkzdnd1bxptzlg2""".splitlines()]
# The deployed 3x3 MDS matrix, as base-36 field elements.
# MDS matrix of the deployed Orchard parameter set, as base-36 field elements
MDS = [[int(x, 36) for x in line.split()] for line in """\
9lyr3qqygws493oncql70kk34wqfjwj1fwtyimaddwqd5uwyr 18h44ta02ssx7gc6xjwxh5qmkicw21rx2rjjtrrwwj9dwgnxwe 6ydbwhyzpt22v2wys1ior0fu7mos1459dhc51o1tak2kmvial
vks39flo760q4sctvf1g1su11v1kgxc452ekgwy7j9zrndw1o xwr1ozfgdenxpacktxxa7rn5b1caorlanku61klsxdql04f8u vd911mx6vsmuifoe8z7kqitut20oqm79sohg5a5aw7wl3u0e2
15f5aekp7aurc4ojqytx16u51s2b2e2vm8zcpg2ujf1jqt257o q43t1ap627ur02qdohyqmpa3jrmw6h5drkhlh6pyf1evyi1k4 1hszwmz3xsk960swavklaa9jviy3o3pvg0br1beh3x7q9g8nw1""".splitlines()]
def inv(x):
  return pow(x % P, P - 2, P)
def mat_vec(M, v):
  return [sum(M[i][j] * v[j] for j in range(len(v))) % P for i in range(len(M))]
def mat_mul(A, B):
  n, m, k_len = len(A), len(B[0]), len(B)
  return [[sum(A[i][k] * B[k][j] for k in range(k_len)) % P for j in range(m)] for i in range(n)]
def mat_inv_2(M):
  iv = inv((M[0][0] * M[1][1] - M[0][1] * M[1][0]) % P)
  return [[M[1][1] * iv % P, (-M[0][1]) * iv % P], [(-M[1][0]) * iv % P, M[0][0] * iv % P]]
C0 = pow((1 << 65) + RC[0][2], 5, P)
A_LINE = MDS[0][1] % P
B_LINE = (-MDS[0][0]) % P
DET12 = (MDS[1][0] * MDS[2][1] - MDS[1][1] * MDS[2][0]) % P
RHS1 = -(MDS[1][2] * C0 + RC[1][1]) % P
RHS2 = -(MDS[2][2] * C0 + RC[1][2]) % P
U0_LINE = (RHS1 * MDS[2][1] - RHS2 * MDS[1][1]) * inv(DET12) % P
V0_LINE = (MDS[1][0] * RHS2 - MDS[2][0] * RHS1) * inv(DET12) % P
S1_0 = (MDS[0][0] * U0_LINE + MDS[0][1] * V0_LINE + MDS[0][2] * C0 + RC[1][0]) % P
L1_LINE = (MDS[1][0] * A_LINE + MDS[1][1] * B_LINE) % P
L2_LINE = (MDS[2][0] * A_LINE + MDS[2][1] * B_LINE) % P
S1_0_5 = pow(S1_0, 5, P)
L1_5 = pow(L1_LINE, 5, P)
L2_5 = pow(L2_LINE, 5, P)
A2_VEC = [(MDS[i][0] * S1_0_5 + RC[2][i]) % P for i in range(3)]
B_VEC = [(MDS[i][1] * L1_5 + MDS[i][2] * L2_5) % P for i in range(3)]
D_VEC = [A2_VEC[i] * inv(B_VEC[i]) % P for i in range(3)]
def line_message(W):
  tau = pow(W % P, INV5, P)
  U = (U0_LINE + A_LINE * tau) % P
  V = (V0_LINE + B_LINE * tau) % P
  m0 = (pow(U, INV5, P) - RC[0][0]) % P
  m1 = (pow(V, INV5, P) - RC[0][1]) % P
  return m0, m1
def build_base_constants(r=54):
  s2 = [B_VEC[i] % P for i in range(3)]
  e1 = (D_VEC[1] - D_VEC[0]) % P
  e2 = (D_VEC[2] - D_VEC[0]) % P
  s2_5 = [pow(s2[i], 5, P) for i in range(3)]
  s3 = [MDS[i][0] * s2_5[0] % P for i in range(3)]
  m2 = [[MDS[i][j] * s2_5[j] * inv(s3[i]) % P for j in range(3)] for i in range(3)]
  c3 = [RC[3][i] * inv(s3[i]) % P for i in range(3)]
  s3_5 = [pow(s3[i], 5, P) for i in range(3)]
  M22 = [[MDS[1][1], MDS[1][2]], [MDS[2][1], MDS[2][2]]]
  M0_12 = [MDS[0][1], MDS[0][2]]
  M12_0 = [MDS[1][0], MDS[2][0]]
  P_mat = [[1, 0], [0, 1]]
  for _ in range(r):
    P_mat = mat_mul(M22, P_mat)
  P_inv = mat_inv_2(P_mat)
  H0_raw = mat_mul(P_mat, [[MDS[1][j] * s3_5[j] % P for j in range(3)],
                             [MDS[2][j] * s3_5[j] % P for j in range(3)]])
  s60_1, s60_2 = H0_raw[0][0] % P, H0_raw[1][0] % P
  a3_h1 = [H0_raw[0][j] * inv(s60_1) % P for j in range(3)]
  a3_h2 = [H0_raw[1][j] * inv(s60_2) % P for j in range(3)]
  sp = [0] * (r + 1)
  sp[0] = MDS[0][0] * s3_5[0] % P
  a3_u0 = [MDS[0][j] * s3_5[j] * inv(sp[0]) % P for j in range(3)]
  c_p, w_p, v_p = [0] * r, [None] * r, [None] * r
  Q_k = [[P_inv[0][0] * s60_1 % P, P_inv[0][1] * s60_2 % P],
           [P_inv[1][0] * s60_1 % P, P_inv[1][1] * s60_2 % P]]
  q_k = [RC[4][1] % P, RC[4][2] % P]
  rc0_cur = RC[4][0] % P
  sched_p = list(range(4, 4 + r)) + [60]
  for k in range(r):
    c_p[k] = rc0_cur * inv(sp[k]) % P
    z_scale = pow(sp[k], 5, P)
    nxt_rc = RC[sched_p[k + 1]]
    sp[k + 1] = MDS[0][0] * z_scale % P
    M0_Qk = [(M0_12[0] * Q_k[0][j] + M0_12[1] * Q_k[1][j]) % P for j in range(2)]
    w_p[k] = [M0_Qk[j] * inv(sp[k + 1]) % P for j in range(2)]
    rc0_cur = (M0_12[0] * q_k[0] + M0_12[1] * q_k[1] + nxt_rc[0]) % P
    Q_next = mat_mul(M22, Q_k)
    v_p[k] = mat_vec(mat_inv_2(Q_next), [M12_0[0] * z_scale % P, M12_0[1] * z_scale % P])
    q_k = [(M22[0][0] * q_k[0] + M22[0][1] * q_k[1] + nxt_rc[1]) % P,
               (M22[1][0] * q_k[0] + M22[1][1] * q_k[1] + nxt_rc[2]) % P]
    Q_k = Q_next
  s_full = [sp[r], s60_1, s60_2]
  c60 = [rc0_cur * inv(s_full[0]) % P, q_k[0] * inv(s_full[1]) % P, q_k[1] * inv(s_full[2]) % P]
  full_m, full_c = [], []
  for rnd in (60, 61, 62):
    s_5 = [pow(s_full[j], 5, P) for j in range(3)]
    s_next = [MDS[i][0] * s_5[0] % P for i in range(3)]
    full_m.append([[MDS[i][j] * s_5[j] * inv(s_next[i]) % P for j in range(3)] for i in range(3)])
    full_c.append([RC[rnd + 1][i] * inv(s_next[i]) % P for i in range(3)])
    s_full = s_next
  s63_5 = [pow(s_full[j], 5, P) for j in range(3)]
  outscale = MDS[0][0] * s63_5[0] % P
  alpha63 = [MDS[0][j] * s63_5[j] * inv(outscale) % P for j in range(3)]
  flat = [e1, e2]
  for i in range(3):
    flat.extend([m2[i][1], m2[i][2], c3[i]])
  flat.extend([a3_u0[1], a3_u0[2], a3_h1[1], a3_h1[2], a3_h2[1], a3_h2[2]])
  for k in range(r):
    flat.extend([c_p[k], w_p[k][0], w_p[k][1], v_p[k][0], v_p[k][1]])
  flat.extend(c60)
  for idx_f in range(3):
    for i in range(3):
      flat.extend([full_m[idx_f][i][1], full_m[idx_f][i][2], full_c[idx_f][i]])
  flat.extend([alpha63[1], alpha63[2]])
  return {'flat': flat, 'outscale': outscale, 'r': r}
BASE_R = build_base_constants(54)
def scale_step_constants(rho0, base=BASE_R):
  r = base['r']
  flat = list(base['flat'])
  inv_rho0 = pow(rho0, P - 2, P)
  flat[0] = (flat[0] * inv_rho0) % P
  flat[1] = (flat[1] * inv_rho0) % P
  inv_r5 = pow(inv_rho0, 5, P)
  r5 = pow(rho0, 5, P)
  flat[4] = (flat[4] * inv_r5) % P
  flat[7] = (flat[7] * inv_r5) % P
  flat[10] = (flat[10] * inv_r5) % P
  r_h = pow(r5, 5, P)
  inv_r_h = pow(inv_r5, 5, P)
  r_sp, inv_sp = r_h, inv_r_h
  for k in range(r):
    cb = 17 + 5 * k
    flat[cb + 0] = (flat[cb + 0] * inv_sp) % P
    r_sp = pow(r_sp, 5, P)
    inv_sp = pow(inv_sp, 5, P)
    w_sc = (r_h * inv_sp) % P
    v_sc = (r_sp * inv_r_h) % P
    flat[cb + 1] = (flat[cb + 1] * w_sc) % P
    flat[cb + 2] = (flat[cb + 2] * w_sc) % P
    flat[cb + 3] = (flat[cb + 3] * v_sc) % P
    flat[cb + 4] = (flat[cb + 4] * v_sc) % P
  cb60 = 17 + 5 * r
  flat[cb60 + 0] = (flat[cb60 + 0] * inv_sp) % P
  flat[cb60 + 1] = (flat[cb60 + 1] * inv_r_h) % P
  flat[cb60 + 2] = (flat[cb60 + 2] * inv_r_h) % P
  r_h5 = pow(r_h, 5, P)
  for idx_f in range(3):
    inv_sp = pow(inv_sp, 5, P)
    r_sp = pow(r_sp, 5, P)
    m_sc = (r_h5 * inv_sp) % P if idx_f == 0 else 1
    for i in range(3):
      cb = 20 + 5 * r + 9 * idx_f + 3 * i
      if idx_f == 0:
        flat[cb + 0] = (flat[cb + 0] * m_sc) % P
        flat[cb + 1] = (flat[cb + 1] * m_sc) % P
      flat[cb + 2] = (flat[cb + 2] * inv_sp) % P
  r_sp = pow(r_sp, 5, P)
  outscale = (base['outscale'] * r_sp) % P
  return flat, outscale
ROUND_COUNT = 54                 # partial rounds of this instance
def eval_step(x, c, r=None):
  """The (135 + 12 r)-operation equivalent step, constants indexed from r (49 + 5 r entries)."""
  r = ROUND_COUNT if r is None else r
  u0 = x % P
  u1 = (u0 + c[0]) % P
  u2 = (u0 + c[1]) % P
  z0, z1, z2 = pow(u0, 5, P), pow(u1, 5, P), pow(u2, 5, P)
  u0 = (z0 + c[2] * z1 + c[3] * z2 + c[4]) % P
  u1 = (z0 + c[5] * z1 + c[6] * z2 + c[7]) % P
  u2 = (z0 + c[8] * z1 + c[9] * z2 + c[10]) % P
  z0, z1, z2 = pow(u0, 5, P), pow(u1, 5, P), pow(u2, 5, P)
  u0 = (z0 + c[11] * z1 + c[12] * z2) % P
  u1 = (z0 + c[13] * z1 + c[14] * z2) % P
  u2 = (z0 + c[15] * z1 + c[16] * z2) % P
  for k in range(r):
    cb = 17 + 5 * k
    u0 = (u0 + c[cb]) % P
    z0 = pow(u0, 5, P)
    u0 = (z0 + c[cb + 1] * u1 + c[cb + 2] * u2) % P
    u1 = (u1 + c[cb + 3] * z0) % P
    u2 = (u2 + c[cb + 4] * z0) % P
  b = 17 + 5 * r
  u0 = (u0 + c[b]) % P
  u1 = (u1 + c[b + 1]) % P
  u2 = (u2 + c[b + 2]) % P
  for cb in (b + 3, b + 12, b + 21):
    z0, z1, z2 = pow(u0, 5, P), pow(u1, 5, P), pow(u2, 5, P)
    u0 = (z0 + c[cb] * z1 + c[cb + 1] * z2 + c[cb + 2]) % P
    u1 = (z0 + c[cb + 3] * z1 + c[cb + 4] * z2 + c[cb + 5]) % P
    u2 = (z0 + c[cb + 6] * z1 + c[cb + 7] * z2 + c[cb + 8]) % P
  z0, z1, z2 = pow(u0, 5, P), pow(u1, 5, P), pow(u2, 5, P)
  return (z0 + c[b + 30] * z1 + c[b + 31] * z2) % P
EXIT_CODES = {
  'success': 0, 'no-repeat': 1, 'table-full': 2, 'gap-width': 3,
  'positioning-cap': 4, 'lockstep-cap': 5, 'start-on-cycle': 6,
}
def derive_coins(seed_hex):
  sb = bytes.fromhex(seed_hex)
  rho0 = int.from_bytes(hashlib.sha256(sb + b":rho0").digest(), "little") % P
  if rho0 == 0:
    rho0 = 1
  x0 = int.from_bytes(hashlib.sha256(sb + b":x0").digest(), "little") % P
  return rho0, x0
def run_reference_trial(rho0_seed, x0_seed, w, K, WG, MCAP, Delta, S, G, GPOS):
  rho0 = rho0_seed % P
  if rho0 == 0:
    rho0 = 1
  mask = (1 << w) - 1
  x = (x0_seed % P) & mask
  x0 = x
  c, outscale = scale_step_constants(rho0)
  gap_lim = 1 << WG
  def f(val):
    return ((eval_step(val, c) * outscale) % P) & mask
  prev_dp_t = 0
  dp_vals = []
  dp_gaps = []
  for block_base in range(0, S, K):
    for j in range(K):
      x = f(x)
      if x < Delta:
        cur_t = block_base + j + 1
        if cur_t > S:
          return 'no-repeat', None, cur_t, len(dp_vals)
        gap = cur_t - prev_dp_t
        if gap >= gap_lim:
          return 'gap-width', None, cur_t, len(dp_vals)
        match_idx = None
        for i, v in enumerate(dp_vals):
          if v == x:
            match_idx = i
            break
        if match_idx is not None:
          g_left = dp_gaps[match_idx]
          x_left = x0 if match_idx == 0 else dp_vals[match_idx - 1]
          g_right = gap
          x_right = dp_vals[-1]
          if g_right < g_left:
            x_left, x_right = x_right, x_left
            g_left, g_right = g_right, g_left
          d_diff = g_right - g_left
          for pos_steps in range(d_diff):
            if pos_steps >= GPOS:
              return 'positioning-cap', None, cur_t, len(dp_vals)
            x_right = f(x_right)
          if x_left == x_right:
            return 'start-on-cycle', None, cur_t, len(dp_vals)
          for lock_steps in range(min(g_left, G)):
            prev_l, prev_r = x_left, x_right
            x_left = f(x_left)
            x_right = f(x_right)
            if x_left == x_right:
              W_l = (rho0 * prev_l - D_VEC[0]) % P
              W_r = (rho0 * prev_r - D_VEC[0]) % P
              return 'success', (line_message(W_l), line_message(W_r)), cur_t, len(dp_vals)
          return 'lockstep-cap', None, cur_t, len(dp_vals)
        if len(dp_vals) >= MCAP:
          return 'table-full', None, cur_t, len(dp_vals)
        dp_vals.append(x)
        dp_gaps.append(gap)
        prev_dp_t = cur_t
  return 'no-repeat', None, S, len(dp_vals)
def main():
  req = json.loads(sys.stdin.read())
  out_trials = []
  for row in req["trials"]:
    idx = row["trial"]
    rho0_s, x0_s = derive_coins(row["seed"])
    st, pair, steps, ndps = run_reference_trial(
      rho0_s, x0_s, w=14, K=23, WG=119, MCAP=64, Delta=512, S=207, G=128, GPOS=255
    )
    if st == "success" and pair is not None:
      (nk_a, rho_a), (nk_b, rho_b) = pair
      ma = (nk_a.to_bytes(32, "little") + rho_a.to_bytes(32, "little")).hex()
      mb = (nk_b.to_bytes(32, "little") + rho_b.to_bytes(32, "little")).hex()
      if ma == mb:
        ma, mb, st = None, None, "start-on-cycle"
    else:
      ma, mb = None, None
    out_trials.append({
      "trial": idx,
      "message_a_hex": ma,
      "message_b_hex": mb,
      "observations": {
        "success": st == "success",
        "steps": steps,
        "stored_dps": ndps,
        "exit_code": EXIT_CODES[st],
      }
    })
  sys.stdout.write(json.dumps({"schema_version": 1, "trials": out_trials}) + "\n")
if __name__ == "__main__":
  main()
