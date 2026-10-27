"""LS1, design X: distinguished-point collision search on sha3-256-r17-prefix-v1 with the design-X message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3), proof.md Section 2:
  v_x = u_x (x < 4), v_4 = XOR_(x<4) rotr(u_x, (ROT[4][2] - ROT[x][2]) mod 64);
  m(u) = 128 bytes = lanes 0..15 of the absorbed state: lane x = v_x ^ K_x, lane 10 + x = v_x ^ K_(10+x) (x = 0..4),
  lanes 5..9 all-ones, lane 15 zero; padding gives lane 16 = 0x8000000000000006.  F(u) = SHA3-256-r17(m(u)) XOR PD
  (PD a fixed 256-bit mask).  m is injective, so F(u) = F(u') with u != u' gives two distinct messages with equal digests.
This program regenerates the bit-sliced straight line of proof.md Section 3 (the same algorithm and node order as the C
generator gen4.c, with the generator's decisions PLAN: constants trial, round-1 and theta complements, the row decisions;
its packed two-address encoding must hash to PROG_SHA256), checks it against a plain implementation, and runs
  rho-w22   : the search of proof.md Section 4 at width 22 (planes 22..255 zeroed after each step), one pair per trial;
              the table keeps the trail number of each end; the replay measures the stored trail by walking it,
              keeping every GCK-th point as a checkpoint, walks the new trail once and lock-steps one segment;
  proj-w256 : eight chained full-width steps from 256 random points, first pair agreeing on the 22 low digest bits.
One Python integer holds a plane for all trials of the request (trial t in bits 256t..256t+255); trials never interact.
This is ls1.py of entry a767dfcf (Jbenisek) with the design-X embedding (consts, build, msg_of) and the rows with one
constant input (eval_selk).
"""
import sys, json, hashlib, heapq, base64, zlib

M64 = (1 << 64) - 1
RCA = [0x1, 0x8082, 0x800000000000808A, 0x8000000080008000, 0x808B, 0x80000001, 0x8000000080008081, 0x8000000000008009,
       0x8A, 0x88, 0x80008009, 0x8000000A, 0x8000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080,
       0x80000001, 0x8000000080008008]
ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
NR = 17                         # rounds of the target
PLANZ = """
eNrtXctyIzey3fsruL8btZu2NQsvABBVBCm2GqTYUmknUWpIQc/whuUJ9v37C+QDmSjJnomxZ6EIKqYtkawHkI+TJx/F+e3X57tfJh8+nn347h+/Tj78NDn8
729/Pzw8Tn6Y/Pbr824/+TD55e7lN/77H4ffvh5+eZicfdd9mJg/9zPv3nx7uzJPKf8O5YX33+Jtea//loxLK+NjsjaahY9hmV/vnFldGHNYzOx2a1KM+TM3
i8nNzNYZsze9XXX+ybynH+dj+bWnl4MxyUT5eG9mCf+ameiKjPK/3uZDZuXNY5gZaxbNFW34+bv+P9XXzz9/1/WT79XZHv7baM/KAssqfNQfHlfGnn2aHdUW
o6ywj2Zn7L6RQP63yZqbwb5tvMv/XTe3O5olrCSZlU1oKvTzAGuQ+38xdvqIJw3lXlsUabn/Fj7P56PkaF/VPOPWuKO5lXdSs09jX8q/a1vVxCI5uzR0cYeH
L8rveaJ72AOJbJf/s72mq10am27w9w7lm+AgT9e9Zu2PRF/+/tIfQSZVZZNyGpz/u2rFlVXJBVH1xwmqb2s6uOSuiGfH2p1H8zn/vsGX56ZvjKL9Ueu86yzc
4qY94gji6FNRx9lj3vJng8eZbr27hHXkfbnjkZY8FPXek4mw2OflvSJiu4bjhjl8tLoktS/ouOIIcKI/jjwur6+PZ+XPbCpnre+kshYQiEWzAJM1bFKjnwv6
V5z0C723Gh8E5+d//snzOXS9LZlJ+UEz6WKWR5ya2bGYW5x5/PyK/v38r706vfU3qno6yd4xZNF1Lil7sFOUL5rUIr+2IhbvjPW3xROy2pb6RnlpZAXD7WyE
9a1MVxo1LkCMFhzmLt/SZzWBtfdpiqYTt406WnQxxQSd7LDqVp10PsCJYH5TNtaquzmjSTkVvRMXmD3RV4md0+8XuP8c76sAMFWVgfrX0zWLvKoU9rj9Aj5l
dpvyax7PYxcNLe/Vz8wl5dWvP/dvKTn48jKGRtU/TLqnQ77NC3gdAdP16ysOlwhsKIEZiqN4PIios75sf3zexbxVyZ36+z6D00O+3qOKD2wuso/1kZF9S5Y3
EOhfu7gvplaA1cy+Hao99VklXTkGZFfFfw+eX3jAEU3ZCHppj92AO9v9ZRbHtW/Fv1OeW/byxdHyuqdVY9NFPQV8szdfFu/pMHTfmnTIcnqhe05zSD4Day/H
exVAfNlPPt9/4+ue3VdV2z8Abq3ucaz+ccLmNFuD1V7CEq0OkwOxhTZ248+0R+A+o1gNYr2bZbDiFZVtzNNLn02BwWuX73FDkrtoLNT6O1vi8LGa3AWKyVx2
68FowO1w2fd2fcb3IUDeVhP36+GG0QMA6ghgC3GCBUti2oLHWf8aESrwK5lA3D3gackMPai0ItysxpujWFMXX+sHTRVk8EnB3td80d1b9OpfALiXLTX6RlX/
NCn7nrfWu6DYe+/s2bwBXPjbD3L81MzG90M13cNes4hhi8WC0ROWErf9jTvqAMC7i2s+BNZxbBgi0qLjiD4W8xAzWPExBG0ZXVZ9VvElinuFnhOL+I+wtw5j
7aeKouW9Jza3geJYQbX0Wd3zmmklqaws6fMcY7KdYeBowIMwfzGypvxHnCPdCvNscqvfY9KTt33Y67ebj6xS9fkE9p5ek25X6cgxUwJv3wDhvM3dIPTjmKk1
bGMB8cWmmNW+EOkXVewGQQbe6g625r+FZV1xy9yRzj29bKrVqwt0sXKKnBH4WRPUxUQ9gX8+9ECMeSXx0x4fXDrvyRQfVYyvDJj5QVl+ec9VYQYt6aus9p3G
1VkccZYcPOxxqvnLZ+QPU0P8x9T4jHKYkemSqoMZaTOMgrUfaRxV/bcJWxl545JfZ5C99+tmnWtZ716r/IYYziMnDkTpQomBmEIebphpMpA5izSn+xYGZjjd
t/Ln9BN6/cCe8lDRIKtlxrGOKFCOp1dI63YM8CPwG9BUYsMJPpW4jNc8+0Kxm2OoZAwowhUjGPw8ZYOKDVX7KomcueoaVr9fEv1b1uRLfjY2VmC/e8uN0YzD
rPFqV704/BsZvqj6w9mEsqoFBuld0fkKqWhGdnvYZl09oB0Eob6FJ9szySaQPhtIsu2Lxojson5Onw/d2isXOW4giygoT583+zyeP86POpCnYg9X1lROtctX
+yRyr1DwGeUea5Rh3uWf0kMVgkBHTgFe7nkPYgPnajXneW/7uvdy++xmV3Ch9b6iyFv5Rt5Dx/yuPw4cYO6Q/BxeVaFcUsUJdnFY2/7nSSI38lqVreYLHNel
JKt0/WEye9sgQDjzp7Sz6/0IMQ4lEt/inXYg4x51sim6nj1tVdQ8SEwgYUBkO2b+WrLNuIpqjwWV70Rf8MbnymdtXJLsel5fLTBY7cpxbbEusuTiyyt5xho1
8322fZeGHenjhpa5pj19lbwgKhMu9nO4npNs5rHlcbTlx3HWXiJ8p7M0a67nlLpl24kungOQCP8ddry37HM1Wsc2u2pJmfudetmH74GE2xF1IB9Z+Ky37ilk
vDsgtgNWhrpWP04Ji8Ghfzz+Tp71UHKM4lN5j1+AsEflLkK4lqqIhrqHxGC4aDb49MLYkteEWDeLZzeIf/vq4wozuoLRmVluWnEcKvb7dWFg+0+wBru7VMzr
TZxVPnyrkxS/TvdSgdlBlSUnJzOgQXa/U3Fjrh2z2DaVEqLN8SqrLpKcFQlP3jUwPSpspcbpSdcfJ9l+vzbVHZ012HEGoX2w0KlhneUAVSufk6152urPS/LW
eyq19BWP/SfE1Zdb8y0ryb4wD7jsjm/njU6tpf9WsTWAz78+/qqu89hUsO46xKPCuvm0wYHPpByvtpJj26EWOykTuOmTXLd87iQ5G9osov5cFqGTTK/IJ4qo
Hjt7yAdvdypWkA2f3bj4qirHNs+6JqNYwV+ujdyldpI0U7dV16Vk1mD0V7ZjW3mXKvfY7b2S5yYf9LrrYWNXKqAzG2/eyvIrDtgXVT099BXqMbHfKNu7ypi/
I//uBXsKv3opNHeF8WLf3CTrc0u+eEHgsCnczXI2Zs/alMLGK7Tr1a1VvMNl2p6PL9nVVYe2PGN76pCOb9Ev0ppVn+99wZR/1haQV2NZl4A2y2v3b9g5xo5j
ud5acTPzGsJfxY+kRE+6/iHr+mXHS2COTLLExsGR7Zb55epapTLrkr3m6xeO1cZG+8bi5bxrhY14bOXs04obM1Xp1CA1X++KTwyzqPmTv4GGQ/WxXdnxJ/Lv
O1z/tOJL8Z/+ifInW0jAwHHjPq9j2Ze63u+L9EFzUOZe82/iYFjZX9Fesx3Wz87XkgtMmcsPihd+0dgkqdqx6DqYf5+EpxbDf5zMxypp+Od//efrX3aldt1f
/8S5zJ///B7+Oll+lUqK/QNlx7e0nXX9eR4mZxNz+qkcBkTy4SSSsUi+P4lkLJKPJ5GMRTI9iWQskh9OIhmL5MeTSMYi+ekkkrFIzk8iGYvkbyeRvKJqJ/r6
WiYn/vpaJicC+1omJwb7WiYnCvtaJg2HbZs8/g/Otu912/aP3iSZnEhsYycz76Bs4tlEygy+xQGciMOF6ZXRWBqrYvF2UKkqXTY5NuH7wZa/QjVBHIyUISFV
4SqNRuxMO4MdLWWyIdkjTMMl6/B6pFe+CtyZi2jHUrTGs1MZ9pTimivD0z5KW8yryRpqjEVDXdF8XqSh7Rl8nl/D8dxWmaKw8j8LFwtlJa7un72uKz0KO+Qj
YKSdVsNNJXppLZ00hLetOegd8k1cfd0evjW4FK/P9/6VyPF9rV8Ll1ykoveAx/bKDlwpdDfNCPcGmJSFpSQ3SXW3oL+oN8Ftq2fPx/doe4Herxt1LBRo8gRD
0kdh2fHmgmfNwHFWLTnRf5tGry9T4WJaeF6kS/D1UQH8LEuiedRkruPISwIUarN7+VNZ8v1B4vcTgIhA+t6QBeJbSb8Prz293pLmwdih12T5OnSkjTxwkRhy
l8kGNFzLfbxUcMrQ+fB6DnaVihfOkt3SJSN9jr8TQpOldYJfOZuhs7qKp3XEAnLl1sYfKlR6alEt6eIP8Na09KpC+ehRXPUFniApXuQEgqAnjP5wB70xh94F
cnCyLgO9Mlj3P0uP0/F1y3jAPKG3OZZjrGhm+fpwCr129foxn8Byi/CbnuTwMEsRcD7DgdK86DNWvbE+PMnT0esA6x1K33tD6+QQAH8FkoOhXvSS5RzKa9DX
MyyJUNQ1erCltRhETrEAnugPlfZM8mU9JX4IiOS91/rzYhdbCo2w3oHa657sk+Vg4LwVAv08lF6ml+s1drOh3vyz2LnF96vdWXyCpvRVD4YnEA6sL4bEU1b3
7iDx40Sgj2fGejLRQCZ4kexGTJRNLeLjn2iSBzyvuEQgV6AJM4RGhtbnCnFOXKYnCmeT9fU+Dq7/zNBF3nRg7yz/yy7IF2cXxnUndPEL+nxp7D7guF1Al7MM
QYlc/EBAzvsn6Mcx1r5SzPK/wUScp0f26Br58b7pPvk3jGni9YdU32f5An4wBHTFXz3hcoUi8jYbaqgaOEQR5PN98ThH8uAQEkgPA4xARsehga5fQ4yEPMsQ
mioUB5ZXcqDn63LkkqEMVEWUycWoIOxZQ96So2Ul6WW8OxFqwRim19C9ZNQjO1mwnQCkiT4Xld+Xp9am5r7o3fGDoo381P5Sse6sH5bjtIzyMeQ+k3z2BIl7
yAESfh5SDZlFP1GFQNZbZEg8FXXeHSROJ+LHnbA1Jy7eugSZJD7aGAiKmA0lpAYdm3aqrMlLVE/CPsvxxXU8Rn2GtGUZNuwYGmBwSUyw4o6wRnARz/cLlY15
ZkUJk7HOVJbDLpPI5V1lN06ghCGy7MfnhHwjpk83xeMRcoBlOnFRgkSUQ6AXe4IuJxBwLBDLULB5zWJTZXFqnb5MiO3gemW/tpHHnUpIC/u9EwgeSK8ZGpl1
yXqUXBVEMWQJC0PWC6NryJpSYafTIuy96BkhuLJrDh1dxFCmoL6FbpIfZ6W4bp40j8SO0Q4khDliqZH076ngcaTjn8o67ti+E4Uq2tFFslvNSmG/HUOlYscS
Iti+87vTEupc2ZdTWQtD4qmm++4g8YdJIKtLlc05UbliNamyNH4wihNcI1DnJZHlREWgtS/PpVg2xagTuiSsiV0mVch05M07MmFmVUtdU7LEsjDx5mfoN8BC
jjWhB4jYpjYxQ1NvIGlT0VKxEQ4dC3h9NGtitZk1fRHoDHUr7EJBEla4fgcFhCAJqcHymBM2xCHoIPKLFYqXDPkJa107grJtQj3eCisH6FoaXWiAQesFQaFA
tgk6YRfoMKlCQ2WF5a2ceN5aglqveKZjls0hSCDOUejYwvmpJvwYQhydn4glAhve03r/r7y+pYdROg21NeGOtdCA5+f7eCpsyPF+FGJ4v5c0aF3un+ybIRIg
f0vXvyv7N3xfkDPbMUIvQ+JpLMnEdwaJpeO0KCbQSW2o48QRXDpDEboI1rByzvmVomrgxJEhURIxmHnfcY0rIYTsAAi55sg1p1ihk2tQ8Ojp3EjtK1UWACa4
pS8rmJGrcM3OSgLqJcGRr3rySbmmclX+Hp9AUA378QBdR1mfJExzKCRI7RUTNrq+k/t15FK1Vhsq1CqoIShysbp4YZ8xr2srbJHZ6TW0i8CFYdGSMDtmrcxO
p5Sop4I2ThJBahdZYeFcU21YqW3YPXciIBGeUUGBa4MXlKjO6BsifLP/AZ+frjVICQV8HMpTandeQp8Xu2zYptNZCOrBFtHsKeTJM6JW7EFl4RwqjFHZg5Um
Ihc0sOYKEM5GS/buV8Kaay2XsyWBxFNH992xxDI2GcSlGrZoAIK4LA4JGpvUpkZ3D7WkSFH+WWqIgSCLINeEygrvpLzPZfvyZ1IuM+iErpOESmpHVhK4QB3B
pdE1MdhPb+aSUDphwZBI+6T3W25WHpeXxLujJQ7U9ukbiAPI8dKGAooY2xpmy2ZbFhOF/aXKYre1BlnbDLHWXvMr3G9qIc5SDdJLDQ71CXxHar3YJjhAaCL5
rgpbcxIaAkE/rcuqGmvDmh7LF6LUkEZtMAsFDyggZPlKjTDUmrCVwocb4MOEIWFFrH4v8kmNvpoEWuT1z5LgbmV98DuHzqHaWy/nqYIMs/YdUu0aKlU7kTTD
SlLsWZWBQ7n+hWQzbtxeOY0lvztIPJ9IIuFrAmc3OlFjNiA1vZI4o0mTiQgYYU3N1JpPW0uSGpFjqOTvvmNTO5QaVJDoS31thrSa4ESV+FnV4ebzUjLpVecy
jNoSDeSGZAfNUjxDEX83X1Ls2UJCF4SlNlDNhQRFiFZ4fheETVPi5Ux7XQ+hRBJbKwQHtrBNleV6KTzEmnByTVWV+19o+KgWRjwl0gnZNp70VD+vNbqkaqNc
My4fBgdtJqcKDbEWVpJmdWAl8M0AYdRxdsJqmdVJgcBRTbVv2Huir/KQDriNwn6JbTpo89EXACHL80lNSOTz/06sT7X3YtWPao/xekpHOmIoCHWCAETrJWgE
mQCokHh6LOG//WP/akgsj01ggig1NY7KnVNQ54IexvDN8IRE7QPVstglMwvYZL+q0HEYQQCzNEioFUuMxFYUWwo4teals+uMSpDa9QWqRSEkBMSTObC3qDvX
+eykofqA6yiJoZTxoUPdcSEAoBa+Co1rcNfSweWa2yW5lpMOd6jZr6d92hH6ciI4I0isiagOJdCGsKnW9DDh66kD7Cp7UevvqQa3qBBgE7FK6qzil9h5gWjo
UF/pYSnLBQtJKPsKGfayvFjK8A10hJEtM1schJ1yJxfliPu0arhL1zBru4VDlJMJA0r8cT0YioNTLFdCL4d0YIk+VShW8pLQ/kibWDQsv6n9HqQ9GHU7j9eV
GBJPjyW9O5YIj02FEjY9+C5P323J/BSti9UnGY64bs8R/Upafup9mZJZGt1qlSmdpihmia72aiCRaNq6wQ6ZlsT7rTS92AOd5P5Gqv2Kf2I6DddJTNOgH9HZ
WtzyNH7eTqFwZYEwYx5qPd1SRR6+A3gurcoFYaMa2DzwvqNtBkGDtJwDTG5T5s1FPTXAF2lgk1vTgTw5SdFTuOVjGbBzCfthfSS6G6nVanSskj5Sr+h/tDJo
irQo6YHVqCsutbjqDNuBob4Ex6TnptJgaSBTYtoWdi39nVpcJTscRN+MrVPqw+B1I65/hWkxYZcMygYda72MUIA+uYLgkjV1YNNI5WFZ3p9LbHJ1JMM+yohE
ajLn03OJ7xAUy4B9Dq4pWj2iZ7m5yvM4QY+6cU6syjp7GXUL0aRxxZ7AEggpB3KVk8soXarzGJhzQzPQUi5kmxwfwAgI1XUDvpS7W+lcqBxyK7md1yOCMv3r
BQy9nhOpU+qp5uiqU+SpzMejkeJ0lWAMZsPT6kTwVBNzo5vnvcyLqOn4KAPWnIvTi85WubwUgtYR0XuQ/R2kXBl1kFMdHt5/kvkc/lIxU+ebZO6o6KfoU9Ug
ggwhJJEDjJDuSU8w2rkWEL2DHY6mwr2AJLO4so4IK7XjuSSWu4BUENA+6NHGee0MMoGuehp02TOIPlwNMi5QmVLk2ukgopryCw2KpydY3h8ofj+R+Wk2olqI
2xf9xppV85xt30yGNO0/BtW9FMja7JQKkmTMBezWxGT4EZYobdnyqIeHQo5iCJIFPjZZS1CTQnWYzhAYn0l2JDX8yvSkd8PtQ1gnVA9s0nPsviKFax7paR7d
YNCAHgZmqZlBHqj9Clk9XP8B5oM3qleh78NCG4jxGF24dHpiih+tUY/wuJaZWgaroZGD9CJgXXeSLao2agaBslUnwYwnWLYkX64CbFMdW1jqKoeyr7UGo66R
t5rYgi+93+ohTmPUNz8GYajqkaGkJ8A4a9/XtriVoKPa7avag1OF4wKyqTwvIEHOlczFShUHnnwN8OjSprbjneoBVlA8PcPy/kDx44SNDJjL88i50AkCOvu1
zIQk6jKoUpoYHTfqFDN0+jtXu4ZxxHZcrHZzaAbITct9kWH5ylQHqX6v2wZ17T4EDbYb/bwbN2AfhZEi47UIvlvdHbJhlC4GXRbYj0pXThhp0F0fFRyiBu/9
6HNXqvdWSnMNk1lYPU4oDVNLh+woGMz4IQ5nkjy3x6AI6exBujhF3hbkuT1WkFPpbKhdk6aLM5cxTwDxPkl5RYxn2zyMw3YhMy7eqFKyMy0IWkixefxPuh/c
PQmjh66WRgdnKt/0wpDhEC8gOIjcCWetem6Q0v4qNygPDYH3M4dM5YjysoO2P69KiqevJnmHoDidSI0wiDMH7TTl/UAPxyc9u0utwUXDTKJ2qkjO7WhQjt63
Tg/WtS3U5vGFRIyEQLpOuRBzsD0N7KlZcXqsodOPyxA4HdW0TtcMJqrcNNX0G9fh5bEFYRjgbHN54hHS7tsRg3Yil0Ez2aGZ1SZG1sNDc+rh2wLa5SIbo76n
Hx4PiQAiq/q9E7hPAMWBBhD/h/bvTTtO7TXz59l4O+ojYFqYYv2/pJLHi8r/f2nz5F+pCFj5XodHqAU3mYOMNKivFHkWEG1m7qW84PkxGelnGDUAKKMMwuCZ
4WNZxmpQjirtjvx/86fIQAPid6L//Qi0eToLmSfM7EvNdMflCS9P9p2+m+gdgmIZtF8mq5iAqelBjeTNaF3QTUGn8cQQw0OnLWBipWZlR6DJ4KNqQzDqaKWG
Y0fG3usaoWrEWGGey7LotcFvWDDyDQHPPF9C/+dKQe9D1USfR+DhjZrjkLkiWxsm5PzP0ksJxDBeTyf7xvmk87xovqkh0agfg0SoYLyQcpiTdC1RY0C+v8ZJ
rQtued3UvJoacZI0M2pmbES/8HtWnP9a5GJ1A4xregiyzQMfUR6PZzkc6zOBeH+2lyCNE11TtEHPc3kNcoz3ilnLN3x0QT8VsIWGk4AyNrSSVY/1h7bh00v6
XXYaVI0dv8EkVLvi0Us1iirp8+lJlncFiv8P3AxCzA==
"""
PLAN = zlib.decompress(base64.b64decode("".join(PLANZ.split()))).decode()   # the plan text (plan.txt with its bit fields in base64), zlib-compressed

PL = {}
_d = lambda t: base64.b64decode(t).hex()   # the bit fields of PLAN are stored in base64 (plan.txt holds them in hex)
for _ln in PLAN.strip().split("\n"):
    _t = _ln.split()
    if _t[0] == "trial": PL[_t[0]] = _t[1]
    elif _t[0] in ("F1", "G1"): PL[_t[0]] = _d(_t[1])
    elif _t[0] == "FG": PL[("FG", int(_t[1]))] = (_d(_t[2]), _d(_t[3]))
    elif _t[0] == "PHI": PL[("PHI", int(_t[1]))] = _d(_t[2])
    elif _t[0] == "DEC": PL[("DEC", int(_t[1]))] = _d(_t[2])
    elif _t[0] == "DECE": PL[("DECE", int(_t[1]))] = _d(_t[2])
    elif _t[0] == "nr": PL["optmode"] = int(_t[3])
TRIAL = int(PL["trial"])            # constants of the generator's selected trial
PROG_SHA256 = "c460716550a7fbbdb7a856225d067fe13e929db65da0b026fc2d0a479df8489f"
NINSTR = 97242
NREG = 2304
B35 = {}                            # LRS: first node of the last round; DIAG: lanes 0, 6, 12, 18, 24 after round NR-2
NC = -1
O_IN, O_XOR, O_AND, O_OR, O_NOT = 0, 1, 2, 3, 4


def consts(trial):
    """Constants of the generator's selected trial (design X, proof.md Section 2): lanes 5..9 all-ones, lane 15 zero, lane 16 the
    padding, lane x = c_x and lane 10 + x = c_x ^ K_x with K_x = 0x5555...55 ^ (lane 16 for x = 1); c_0..c_4 from xorshift of the
    trial number, exactly as gen4.c set_consts."""
    M = (1 << 64) - 1
    rs = (0x9E3779B97F4A7C15 * trial + 1) & M

    def xs():
        nonlocal rs
        rs ^= (rs << 13) & M; rs ^= rs >> 7; rs ^= (rs << 17) & M
        return rs
    for _ in range(10): xs()
    K = [0] * 25
    K[16] = 0x8000000000000006
    for x in range(5):
        c = xs(); k = 0x5555555555555555 ^ (K[16] if x == 1 else 0)
        K[x], K[10 + x], K[5 + x] = c, c ^ k, M
    return K


KL = consts(TRIAL)


# ---------------- generator (same algorithm and node order as gen.c) ----------------
class Gen:
    def __init__(self):
        self.op, self.a, self.b, self.k, self.lin = [], [], [], [], []
        self.form, self.fidx, self.cons = [], {}, {}

    def new(self, op, a, b):
        self.op.append(op); self.a.append(a); self.b.append(b); self.k.append(0); self.lin.append(-1)
        return len(self.op) - 1

    def consn(self, op, a, b):
        if op != O_NOT and a > b: a, b = b, a
        key = (op, a, b)
        n = self.cons.get(key)
        if n is None:
            n = self.new(op, a, b); self.cons[key] = n
        return n

    def fadd(self, m, node):
        f = len(self.form); self.form.append((m, node)); self.fidx[m] = f
        return f

    def xorv(self, a, b):
        if a[0] == NC: return (b[0], b[1] ^ a[1])
        if b[0] == NC: return (a[0], a[1] ^ b[1])
        if a[0] == b[0]: return (NC, a[1] ^ b[1])
        la, lb = self.lin[a[0]], self.lin[b[0]]
        if la >= 0 and lb >= 0:
            m = self.form[la][0] ^ self.form[lb][0]
            kk = self.k[a[0]] ^ self.k[b[0]]
            if m == 0: return (NC, kk ^ a[1] ^ b[1])
            f = self.fidx.get(m)
            if f is not None:
                n3 = self.form[f][1]
                return (n3, kk ^ a[1] ^ b[1] ^ self.k[n3])
            n = self.new(O_XOR, min(a[0], b[0]), max(a[0], b[0]))
            self.k[n] = kk; self.lin[n] = self.fadd(m, n)
            return (n, a[1] ^ b[1])
        return (self.consn(O_XOR, a[0], b[0]), a[1] ^ b[1])

    def notv(self, a):
        if a[0] == NC: return a
        before = len(self.op)
        n = self.consn(O_NOT, a[0], 0)
        if len(self.op) > before and self.lin[a[0]] >= 0:
            self.lin[n] = self.lin[a[0]]; self.k[n] = self.k[a[0]] ^ 1
        return (n, a[1] ^ 1)

    def and2(self, a, b, sel=0):
        """logical a AND b; a mixed-polarity term is A ^ (A & B) (polarity 0) or, with sel, (NOT A) | B (polarity 1)"""
        if a[0] == NC: return b if a[1] else (NC, 0)
        if b[0] == NC: return a if b[1] else (NC, 0)
        if a[0] == b[0]: return a if a[1] == b[1] else (NC, 0)
        if a[1] == 0 and b[1] == 0: return (self.consn(O_AND, a[0], b[0]), 0)
        if a[1] == 1 and b[1] == 1: return (self.consn(O_OR, a[0], b[0]), 1)
        A, B = (a[0], b[0]) if a[1] == 0 else (b[0], a[0])
        if sel:
            na = self.notv((A, 0))
            return (self.consn(O_OR, na[0], B), 1)
        t = self.consn(O_AND, A, B)
        return self.xorv((A, 0), (t, 0))


def cost_term(b1, b2):
    if b1[0] == NC or b2[0] == NC or b1[0] == b2[0]: return 0
    return 1 if (b1[1] ^ 1) == b2[1] else 2


def row_choose(b, need):
    """the row decision of gen3.c: complement subset s and 10-gate position j (-1: none), first cheapest"""
    distinct = all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5
    best, bc, bj = -1, 1 << 30, -1
    for j in range(-1, 5 if distinct else 0):
        if j >= 0 and not ((need >> j) & 1 and (need >> ((j + 1) % 5)) & 1): continue
        for s in range(32):
            c = 0; bb = list(b)
            for X in range(5):
                if s >> X & 1:
                    if b[X][0] == NC: c = 1 << 29
                    else: bb[X] = (b[X][0], b[X][1] ^ 1); c += 1
            for X in range(5):
                if need >> X & 1:
                    if X == j:
                        k = (j + 1) % 5; p1, p2 = bb[(k + 1) % 5], bb[(k + 2) % 5]
                        if (p1[1] ^ 1) == p2[1]: c += cost_term((bb[k][0], bb[k][1] ^ (p1[1] ^ 1)), bb[(X + 2) % 5])
                        else: c += 1                                   # mixed term k: its output polarity is free
                    else: c += cost_term(bb[(X + 1) % 5], bb[(X + 2) % 5])
            if c < bc: bc, best, bj = c, s, j
    return best, bj


TAB = {}
for _L in (0, 1):
    for _p in range(32):
        TAB[(_L, _p)] = row_choose([(X, (_p >> X) & 1) for X in range(5)], 0x0F if _L else 0x1F)


def row_order(T):
    """gen3.c row_order: chain bases first (X not in T, X-1 in T), then each X after the output X+1 it reads"""
    done, ordr = 0, []
    for X in range(5):
        if (T >> ((X + 4) % 5)) & 1 and not (T >> X) & 1: ordr.append(X); done |= 1 << X
    for X in range(5):
        st, Y = [], X
        while not (done >> Y) & 1:
            st.append(Y)
            if not (T >> Y) & 1: break
            Y = (Y + 1) % 5
        while st:
            Z = st.pop()
            if not (done >> Z) & 1: ordr.append(Z); done |= 1 << Z
    return ordr


def eval_selc(pat, s, T, mc):
    """the term polarities of a planned row with trick set T (gen3.c eval_row, chained form): out[X] reads out[X+1] for X in T"""
    bb = [((pat >> X) & 1) ^ ((s >> X) & 1) for X in range(5)]
    sel, ns, bit = [0] * 5, [0] * 5, 0
    for X in row_order(T):
        a, b = (ns[(X + 1) % 5] if (T >> X) & 1 else bb[(X + 1) % 5]) ^ 1, bb[(X + 2) % 5]
        if a == b: tp = a
        else: tp = (mc >> bit) & 1; bit += 1; sel[X] = tp
        ns[X] = bb[X] ^ tp
    return sel


def eval_selk(k, pat, s, T, mc):
    """the term polarities of a planned row whose input k is the constant bit k of pat (gen4.c eval_rowc): values are constants
    (node -1) or nodes with a polarity; and2 and xor fold constants as the generator does"""
    bb = []
    nid = 5
    for X in range(5):
        if X == k: bb.append((-1, (pat >> X) & 1))
        elif (s >> X) & 1: bb.append((nid, ((pat >> X) & 1) ^ 1)); nid += 1
        else: bb.append((X, (pat >> X) & 1))
    sel, ns, bit = [0] * 5, [None] * 5, 0
    for X in row_order(T):
        a = ns[(X + 1) % 5] if (T >> X) & 1 else bb[(X + 1) % 5]
        a = (a[0], a[1] ^ 1); b = bb[(X + 2) % 5]
        if a[0] < 0: t = b if a[1] else (-1, 0)
        elif b[0] < 0: t = a if b[1] else (-1, 0)
        elif a[0] == b[0]: t = a if a[1] == b[1] else (-1, 0)
        elif a[1] == b[1]: t = (nid, a[1]); nid += 1
        else: ch = (mc >> bit) & 1; bit += 1; sel[X] = ch; t = (nid, ch); nid += 1
        x = bb[X]
        if t[0] < 0: o = (x[0], x[1] ^ t[1])
        elif x[0] < 0: o = (t[0], t[1] ^ x[1])
        elif x[0] == t[0]: o = (-1, x[1] ^ t[1])
        else: o = (nid, x[1] ^ t[1]); nid += 1
        ns[X] = o
    return sel


def bits(h, n):
    v = int.from_bytes(bytes.fromhex(h), "little")
    return [(v >> i) & 1 for i in range(n)]


def build():
    g = Gen()
    for j in range(256):
        n = g.new(O_IN, 0, 0); g.lin[n] = g.fadd(1 << j, n)
    S = [[(NC, (KL[l] >> z) & 1) for z in range(64)] for l in range(25)]
    vv = [[(64 * x + z, 0) for z in range(64)] for x in range(4)] + [[None] * 64]
    for w in range(64):                                  # v_4[w] = XOR_(x<4) v_x[w + R4 - Rx]: XOR_x rotl(v_x, ROT[x][2]) = 0
        a = (NC, 0)
        for x in range(4): a = g.xorv(a, vv[x][(w + ROT[4][2] - ROT[x][2]) & 63])
        vv[4][w] = a
    for x in range(5):
        for z in range(64):
            S[x][z] = g.xorv(vv[x][z], (NC, (KL[x] >> z) & 1)); S[10 + x][z] = g.xorv(vv[x][z], (NC, (KL[10 + x] >> z) & 1))
    for r in range(NR):
        last = r == NR - 1
        if r == 1: ff, gg = list(bytes.fromhex(PL["F1"])), bits(PL["G1"], 320)           # ff: the 5-bit D masks of the 320 lanes (x, z)
        elif r >= 2: ff, gg = list(bytes.fromhex(PL[("FG", r)][0])), bits(PL[("FG", r)][1], 320)
        else: ff = gg = [0] * 320
        phi = bits(PL[("PHI", r)], 1600)
        dec = dece = None
        if PL.get("optmode", 3) >= 4 and (r >= 2 or (r == 1 and PL.get("optmode", 3) >= 5)) and not last and ("DEC", r) in PL:
            hb = bytes.fromhex(PL[("DEC", r)]); dec = [hb[2 * i] | hb[2 * i + 1] << 8 for i in range(320)]
            dece = list(bytes.fromhex(PL[("DECE", r)]))                                  # the output complements E of the 320 rows
        C = [[None] * 64 for _ in range(5)]
        D_ = [[None] * 64 for _ in range(5)]
        D2 = [[None] * 64 for _ in range(5)]                          # D2 = NOT D, built once for a lane whose mask is not 0
        for x in range(5):
            s = S[x][63]
            for y in range(1, 5): s = g.xorv(s, S[x + 5 * y][63])
            C[x][63] = g.notv(s) if gg[x * 64 + 63] else s
        for z in range(64):
            if z < 63:
                for x in range(5):
                    s = S[x][z]
                    for y in range(1, 5): s = g.xorv(s, S[x + 5 * y][z])
                    C[x][z] = g.notv(s) if gg[x * 64 + z] else s
            for x in range(5):
                D_[x][z] = g.xorv(C[(x + 4) % 5][z], C[(x + 1) % 5][(z + 63) & 63])
                D2[x][z] = g.notv(D_[x][z]) if ff[x * 64 + z] else D_[x][z]
        NS = [row[:] for row in S]
        nY, need = (1, 0x0F) if last else (5, 0x1F)
        for Y in range(nY):
            for z in range(64):
                b = []
                for X in range(5):
                    y, x = X, (3 * Y + X) % 5
                    zz = (z - ROT[x][y]) & 63
                    b.append(g.xorv(S[x + 5 * y][zz], D2[x][zz] if (ff[x * 64 + zz] >> y) & 1 else D_[x][zz]))
                rsel = None
                distinct = all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5
                kc = [X for X in range(5) if b[X][0] == NC]
                onec = kc[0] if len(kc) == 1 and len(set(v[0] for v in b if v[0] != NC)) == 4 else -1
                if dec is not None and (distinct or (onec >= 0 and r == 1)):
                    dd = dec[Y * 64 + z]; best, Tm = dd & 31, (dd >> 5) & 31
                    pat = sum(v[1] << X for X, v in enumerate(b))
                    rsel = eval_selc(pat, best, Tm, dd >> 10) if distinct else eval_selk(onec, pat, best, Tm, dd >> 10)
                    for X in range(5):
                        if best >> X & 1: b[X] = g.notv(b[X])
                    for X in row_order(Tm):                          # chained row: out[X] reads the finished out[X+1] for X in Tm
                        if not need >> X & 1: continue
                        t1 = NS[(X + 1) % 5 + 5 * Y][z] if (Tm >> X) & 1 else b[(X + 1) % 5]
                        NS[X + 5 * Y][z] = g.xorv(b[X], g.and2((t1[0], t1[1] ^ 1), b[(X + 2) % 5], rsel[X]))
                    for X in range(5):                               # output complements E of the row, after its five outputs
                        if (dece[Y * 64 + z] >> X) & 1: NS[X + 5 * Y][z] = g.notv(NS[X + 5 * Y][z])
                    continue
                elif all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5:
                    best, bj = TAB[(int(last), sum(v[1] << X for X, v in enumerate(b)))]
                else:
                    best, bj = row_choose(b, need)
                for X in range(5):
                    if best >> X & 1: b[X] = g.notv(b[X])
                k = (bj + 1) % 5
                if bj >= 0:                                          # 10-gate row: output bj reads output k
                    p1, p2 = b[(k + 1) % 5], b[(k + 2) % 5]
                    sel = ((b[(bj + 2) % 5][1] ^ 1) ^ b[k][1]) if (p1[1] ^ 1) != p2[1] else 0
                    if rsel is not None: sel = rsel[k]
                    NS[k + 5 * Y][z] = g.xorv(b[k], g.and2((p1[0], p1[1] ^ 1), p2, sel))
                for X in range(5):
                    if need >> X & 1:
                        if bj >= 0 and X == k: continue
                        t1 = NS[k + 5 * Y][z] if X == bj else b[(X + 1) % 5]     # not y and z == not chi_y and z
                        t = g.and2((t1[0], t1[1] ^ 1), b[(X + 2) % 5], phi[(X + 5 * Y) * 64 + z] if rsel is None else rsel[X])
                        NS[X + 5 * Y][z] = g.xorv(b[X], t)
        for z in range(64):
            NS[0][z] = (NS[0][z][0], NS[0][z][1] ^ ((RCA[r] >> z) & 1))
        S = NS
        if r == 1 and not last: S = cut_pass(g, S)
        if r == NR - 2:
            B35["LRS"] = len(g.op)
            B35["DIAG"] = {S[l][z][0] for l in (0, 6, 12, 18, 24) for z in range(64) if S[l][z][0] != NC}
    out = [S[j >> 6][j & 63] for j in range(256)]
    PD = 0
    for j, v in enumerate(out):
        assert v[0] != NC and v[0] >= 256
        PD |= v[1] << j
    return g, [v[0] for v in out], PD


def cut_pass(g, S):
    """straight-line cuts of rounds 0..1 (gen3.c cut_pass; applied once after round 1, node order kept): (a) NOT(NOT x) = x and a
    second NOT of one value are one node; (b) p XOR (p AND q) = p AND NOT q, p XOR (p OR q) = NOT p AND q when the AND (OR) has no
    other use: the XOR node becomes an AND node on p and a NOT node of the other operand (the operand of that operand when it is a NOT,
    an existing live NOT node defined before the XOR, else the AND/OR node rewritten as a NOT). Returns the remapped state planes."""
    nn = len(g.op); op, a, b = g.op, g.a, g.b
    live = [False] * nn
    for row in S:
        for v in row:
            if v[0] != NC: live[v[0]] = True
    for i in range(nn - 1, 255, -1):
        if live[i]:
            live[a[i]] = True
            if op[i] != O_NOT: live[b[i]] = True
    rp = list(range(nn)); nt = {}; uc = [0] * nn
    for i in range(256, nn):
        if live[i]:
            uc[a[i]] += 1
            if op[i] != O_NOT: uc[b[i]] += 1
    for row in S:
        for v in row:
            if v[0] != NC: uc[v[0]] += 100
    for i in range(256, nn):
        if not live[i]: continue
        o = op[i]; a[i] = rp[a[i]]
        if o != O_NOT: b[i] = rp[b[i]]
        if o == O_NOT:
            x = a[i]
            if x >= 256 and op[x] == O_NOT and live[x]: rp[i] = a[x]; live[i] = False; continue
            if x in nt and live[nt[x]]: rp[i] = nt[x]; live[i] = False; continue
            nt[x] = i; continue
        if o != O_XOR: continue
        for k in range(2):
            p, j = (b[i], a[i]) if k else (a[i], b[i])
            if j < 256 or not live[j] or op[j] not in (O_AND, O_OR): continue
            if a[j] != p and b[j] != p: continue
            if uc[j] != 1: continue
            jop = op[j]
            q = b[j] if a[j] == p else a[j]
            rr, oo = (q, p) if jop == O_AND else (p, q)
            if rr >= 256 and op[rr] == O_NOT: nq = a[rr]; live[j] = False
            elif rr in nt and nt[rr] < i and live[nt[rr]]: nq = nt[rr]; live[j] = False
            else: op[j] = O_NOT; a[j] = rr; b[j] = 0; nt[rr] = j; nq = j
            op[i] = O_AND
            if jop == O_AND: a[i], b[i] = oo, nq
            else: a[i], b[i] = nq, oo
            break
    g.cons = {}
    return [[(v[0] if v[0] == NC else rp[v[0]], v[1]) for v in row] for row in S]


def allocate(g, outn):
    nn = len(g.op)
    live = [False] * nn
    for n in outn: live[n] = True
    for i in range(nn - 1, 255, -1):
        if live[i]:
            live[g.a[i]] = True
            if g.op[i] != O_NOT: live[g.b[i]] = True
    last = [0] * nn
    for i in range(256, nn):
        if live[i]:
            last[g.a[i]] = i
            if g.op[i] != O_NOT: last[g.b[i]] = i
    outj = {}
    for j, n in enumerate(outn): last[n] = 0xFFFF; outj[n] = j
    outdef = list(outn)
    reg = [0] * nn
    busy = [False] * NREG
    LRS, DIAG = B35["LRS"], B35["DIAG"]
    hfree = list(range(256, NREG))                    # free registers 256.. (a heap; only allocation takes them)
    lfree = []                                        # free registers 0..255 (a heap; may hold busy or repeated entries)
    for j in range(256):
        reg[j] = j
        if last[j]: busy[j] = True
        else: lfree.append(j)
    heapq.heapify(lfree)
    code, prog, peak = {O_XOR: 0, O_AND: 1, O_OR: 2, O_NOT: 3}, [], 0
    for i in range(256, nn):
        if not live[i]: continue
        op, a = g.op[i], g.a[i]
        b = a if op == O_NOT else g.b[i]
        dy = []                                       # registers of the operands that die here
        for k, o in enumerate((a, b)):
            if k == 1 and o == a: break
            if last[o] == i:
                r = reg[o]; busy[r] = False; dy.append(r)
                heapq.heappush(lfree if r < 256 else hfree, r)
        if i in outj:
            d = outj[i]; assert not busy[d]
        else:                                         # the lowest free register this value may use (gen3.c, B35)
            ok = [r for r in dy if r >= 256 or (i < LRS and i not in DIAG) or (i >= LRS and outdef[r] >= last[i])]
            d = min(ok) if ok else None               # a dying operand's register first (destination = a)
            if d is not None: pass
            elif i >= LRS:
                d = next((r for r in range(256) if not busy[r] and outdef[r] >= last[i]), None)
            elif i not in DIAG:
                while lfree and busy[lfree[0]]: heapq.heappop(lfree)
                if lfree: d = heapq.heappop(lfree)
            if d is None:
                while busy[hfree[0]]: heapq.heappop(hfree)
                d = heapq.heappop(hfree)
        busy[d] = True; reg[i] = d; peak = max(peak, d + 1)
        prog.append((code[op], d, reg[a], 0 if op == O_NOT else reg[g.b[i]]))
    return prog, peak


def encode(prog):
    """two-address encoding, packed little-endian: bits 0-1 op, bit 2 t; t = 1: destination = a, then a and (not NOT) b;
    t = 0: d, a and (not NOT) b; registers 11 bits.  A binary instruction with destination b is written with a, b swapped."""
    out = bytearray(); acc = nb = 0
    for c, d, a, b in prog:
        assert max(d, a, b) < 2048
        if c == 3: w, k = (3 | 4 | a << 3, 14) if d == a else (3 | d << 3 | a << 14, 25)
        else:
            if d == b and d != a: a, b = b, a
            w, k = (c | 4 | a << 3 | b << 14, 25) if d == a else (c | d << 3 | a << 14 | b << 25, 36)
        acc |= w << nb; nb += k
        while nb >= 8: out.append(acc & 255); acc >>= 8; nb -= 8
    if nb: out.append(acc)
    return bytes(out)


def compile_prog(prog):
    """The straight line, executed instruction by instruction (opcode 0 XOR, 1 AND, 2 OR, 3 NOT)."""
    P = tuple(prog)

    def step(R, A):
        for c, d, a, b in P:
            if c == 0: R[d] = R[a] ^ R[b]
            elif c == 1: R[d] = R[a] & R[b]
            elif c == 2: R[d] = R[a] | R[b]
            else: R[d] = R[a] ^ A
    return step


# ---------------- reference ----------------
def _perm_src():
    """Keccak-f rounds as straight Python source (theta, rho, pi, chi, iota per round; lanes a0..a24)."""
    L = ["def perm(a, rounds):", " " + ",".join("a%d" % i for i in range(25)) + " = a", " for rc in RCA[:rounds]:"]
    for x in range(5): L.append("  c%d = a%d ^ a%d ^ a%d ^ a%d ^ a%d" % (x, x, x + 5, x + 10, x + 15, x + 20))
    for x in range(5): L.append("  d%d = c%d ^ (((c%d << 1) | (c%d >> 63)) & M64)" % (x, (x + 4) % 5, (x + 1) % 5, (x + 1) % 5))
    for x in range(5):
        for y in range(5):
            r = ROT[x][y]; i = x + 5 * y; o = y + 5 * ((2 * x + 3 * y) % 5)
            L.append("  v = a%d ^ d%d; b%d = %s" % (i, x, o, "(((v << %d) | (v >> %d)) & M64)" % (r, 64 - r) if r else "v"))
    for y in range(5):
        for x in range(5):
            L.append("  a%d = b%d ^ (~b%d & b%d)" % (x + 5 * y, x + 5 * y, (x + 1) % 5 + 5 * y, (x + 2) % 5 + 5 * y))
    L.append("  a0 ^= rc")
    L.append(" a[:] = [" + ",".join("a%d" % i for i in range(25)) + "]")
    L.append(" return a")
    return "\n".join(L)


exec(compile(_perm_src(), "perm", "exec"))


def digest(msg, rounds=NR):
    blk = bytearray(136 * (len(msg) // 136 + 1)); blk[:len(msg)] = msg
    blk[len(msg)] ^= 6; blk[-1] ^= 0x80
    st = [0] * 25
    for o in range(0, len(blk), 136):
        for i in range(17): st[i] ^= int.from_bytes(blk[o + 8 * i:o + 8 * i + 8], "little")
        perm(st, rounds)
    return b"".join(st[i].to_bytes(8, "little") for i in range(4))


def msg_of(u):
    l = [KL[i] for i in range(16)]
    v = [(u >> (64 * i)) & M64 for i in range(4)]
    v4 = 0
    for x in range(4):
        d = (ROT[4][2] - ROT[x][2]) % 64                  # v_4 = XOR_(x<4) rotr(u_x, d_x)
        v4 ^= ((v[x] >> d) | (v[x] << (64 - d))) & M64 if d else v[x]
    v.append(v4)
    for x in range(5):
        l[x], l[10 + x] = v[x] ^ KL[x], v[x] ^ KL[10 + x]
    return b"".join(w.to_bytes(8, "little") for w in l)


def F_ref(u, PD):
    return int.from_bytes(digest(msg_of(u)), "little") ^ PD


# ---------------- setup and checks ----------------
def setup():
    for m in (b"", b"abc", bytes(135), bytes(200)):
        assert digest(m, 24) == hashlib.sha3_256(m).digest()
    g, outn, PD = build()
    prog, peak = allocate(g, outn)
    assert hashlib.sha256(encode(prog)).hexdigest() == PROG_SHA256 and len(prog) == NINSTR and peak <= NREG
    return compile_prog(prog), PD, len(prog)


def to_planes(points, T):
    """points[t][l] (256-bit) -> 256 planes with bit 256 t + l."""
    planes = [0] * 256
    for t in range(T):
        for l, u in enumerate(points[t]):
            g = 256 * t + l
            j = 0
            while u:
                if u & 1: planes[j] |= 1 << g
                u >>= 1; j += 1
    return planes


def lane_value(R, g, width=256):
    v = 0
    for j in range(width):
        v |= ((R[j] >> g) & 1) << j
    return v


def check_step(step, PD):
    import random
    rnd = random.Random(1)
    pts = [[rnd.getrandbits(256) for _ in range(256)]]
    R = [0] * NREG
    R[:256] = to_planes(pts, 1)
    A = (1 << 256) - 1
    cur = pts[0]
    for _ in range(2):
        step(R, A)
        cur = [F_ref(u, PD) for u in cur]
        for l in range(0, 256, 15):
            assert lane_value(R, l) == cur[l]


def shake(data, n):
    return hashlib.shake_256(data).digest(n)


SALT = bytes.fromhex("4f1e109f8e8ebd49662c5122210690bc")          # 16 bytes drawn once when this package was generated; prefixed to every trial seed, so no trial is a function of the public seed alone


# ---------------- rho-w22: the search of proof.md Section 4 at width W ----------------
W, H, DK, DTT, LC, U, TB = 22, 4, 3, 5, 256, 3000, 400      # a DP: bits 0..3 zero and bits 4..6, as a number, < 5; replay cap LC; no trail is cut
GCK = 16                                                    # checkpoint gap of the replay


def rho_w(trials, step, PD):
    T = len(trials)
    A = (1 << (256 * T)) - 1
    mask = (1 << W) - 1
    R = [0] * NREG
    seeds = [SALT + bytes.fromhex(t["seed"]) for t in trials]
    rho, nid, att, astart = [0] * T, [0] * T, [-1] * T, [0] * T
    table = [dict() for _ in range(T)]
    done = [None] * T
    obs = [dict(steps=0, trails=0, attempts=0, stored=0, replay_evals=0) for _ in range(T)]
    lid, lst = [0] * (256 * T), [0] * (256 * T)
    pend = []

    def f_small(u):
        return F_ref(u, PD) & mask

    def is_dp(x):
        return x & ((1 << H) - 1) == 0 and (x >> H) & ((1 << DK) - 1) < DTT

    def new_attempt(t, c):
        att[t] += 1; obs[t]['attempts'] += 1
        rho[t] = int.from_bytes(shake(seeds[t] + att[t].to_bytes(4, 'little'), 8), 'little') & mask
        table[t].clear(); nid[t] = 256; astart[t] = c
        for l in range(256):
            g = 256 * t + l
            lid[g] = l; lst[g] = c
            pend.append((g, (rho[t] + l) & mask))
        obs[t]['trails'] += 256

    def apply_pending():
        if not pend: return
        clr = 0
        for g, _ in pend: clr |= 1 << g
        for j in range(W):
            st = 0
            for g, x in pend:
                if (x >> j) & 1: st |= 1 << g
            R[j] = (R[j] & ~clr & A) | st
        del pend[:]

    def replay(sa, sb, lb, t):
        if lb > LC: return None                        # the new trail is longer than the cap
        a, la, ck = sa, 0, []                          # la: evaluations of the stored trail from its start to its DP;
        while True:                                    # ck: its points a_i for i = 0, GCK, 2 GCK, ... (checkpoints)
            if la % GCK == 0: ck.append(a)
            a = f_small(a); la += 1
            if is_dp(a) or la >= LC: break
        ev = la
        if not is_dp(a):
            obs[t]['replay_evals'] += ev; return None
        d = la - lb                                    # aligned pairs (a_i, b_(i-d))
        if d >= 0:
            ia, a, b = d, ck[d // GCK], sb
            for _ in range(d % GCK): a = f_small(a)
            ev += d % GCK
        else:
            ia, a, b = 0, sa, sb
            for _ in range(-d): b = f_small(b)
            ev += -d
        if a == b:
            obs[t]['replay_evals'] += ev; return None
        nx = (ia // GCK + 1) * GCK
        while nx < la:                                 # walk b to the next checkpoint; equal there: the trails merge in this segment
            q = b
            for _ in range(nx - ia): q = f_small(q)
            ev += nx - ia
            if q == ck[nx // GCK]: break
            a, b, ia, nx = ck[nx // GCK], q, nx, nx + GCK
        r = None
        for _ in range(min(nx, la) - ia):              # lock step through one segment
            na, nb = f_small(a), f_small(b); ev += 2
            if na == nb: r = (a, b); break
            a, b = na, nb
        obs[t]['replay_evals'] += ev
        return r

    for t in range(T): new_attempt(t, 0)
    apply_pending()
    c = 0
    while any(d is None for d in done):
        c += 1
        if c > 4000: raise RuntimeError("no pair")
        step(R, A)
        for j in range(W, 256): R[j] = 0               # width reduction (this experiment only)
        anyv = 0
        for j in range(H): anyv |= R[j]
        dpm = A ^ anyv                                  # walks with the low H bits zero
        eq, lt = dpm, 0                                 # then the DK bits above them, as a number, < DTT (bit-parallel, most significant first)
        for i in range(DK):
            p = R[H + DK - 1 - i]
            if (DTT >> (DK - 1 - i)) & 1: lt |= eq & (A ^ p); eq &= p
            else: eq &= A ^ p
        dpm = lt
        img = [R[j].to_bytes(32 * T, "little") for j in range(W)]          # byte image of the planes 0..W-1 of this step
        events = []
        while dpm:
            low = dpm & -dpm
            events.append(low.bit_length() - 1)
            dpm ^= low
        seen, fresh = set(), set()
        for g in events:
            t = g >> 8
            if g in seen or done[t] is not None or t in fresh: continue
            seen.add(g)
            x = sum(((img[j][g >> 3] >> (g & 7)) & 1) << j for j in range(W))
            ln = c - lst[g]
            tb = table[t]
            if x in tb:
                ida = tb[x]
                if ida != lid[g]:
                    r = replay((rho[t] + ida) & mask, (rho[t] + lid[g]) & mask, ln, t)
                    if r is not None:
                        done[t] = r; obs[t]['steps'] = c - astart[t]; obs[t]['stored'] = len(tb)
                        continue
            else:
                tb[x] = lid[g]
            if nid[t] >= U:
                new_attempt(t, c); fresh.add(t); continue
            i = nid[t]; nid[t] += 1; obs[t]['trails'] += 1
            lid[g] = i; lst[g] = c
            pend.append((g, (rho[t] + i) & mask))
        for t in range(T):
            if done[t] is None and c - astart[t] >= TB: new_attempt(t, c)
        apply_pending()
    return done, obs


# ---------------- proj-w256: chained full-width steps, 22-bit agreement ----------------
def proj_w(trials, step, PD, steps=8, bits=22):
    T = len(trials)
    A = (1 << (256 * T)) - 1
    pts = []
    for tr in trials:
        raw = shake(SALT + bytes.fromhex(tr["seed"]) + b"proj", 32 * 256)
        pts.append([int.from_bytes(raw[32 * l:32 * l + 32], "little") for l in range(256)])
    R = [0] * NREG
    R[:256] = to_planes(pts, T)
    from array import array
    allkeys = []                            # allkeys[s][g]: the 22 low image bits of lane g at step s

    def point(t, l, s):                     # input of step s on lane l (reference chain from the start point)
        u = pts[t][l]
        for _ in range(s): u = F_ref(u, PD)
        return u

    for s in range(steps):
        step(R, A)
        cols = [bin(R[j] | (1 << (256 * T)))[:2:-1] for j in range(bits)]   # bit g of plane j = cols[j][g]
        allkeys.append(array("I", (int("".join(c[g] for c in reversed(cols)), 2) for g in range(256 * T))))
        del cols
    done = [None] * T
    for t in range(T):
        st = {}
        for s in range(steps):
            ks = allkeys[s]
            for l in range(256):
                key = ks[256 * t + l]
                o = st.get(key)
                if o is None:
                    st[key] = (l, s)
                else:
                    a, b = point(t, o[0], o[1]), point(t, l, s)
                    if a != b:
                        done[t] = (a, b, s); break
            if done[t] is not None: break
    return done


def main():
    step, PD, nins = setup()
    check_step(step, PD)
    req = json.load(sys.stdin)
    if req["schema_version"] != 1 or req["target_profile"] != "sha3-256-r%d-prefix-v1" % NR:
        raise ValueError("unexpected organizer target")
    mask = ((1 << 22) - 1).to_bytes(32, "little")
    if req["event"] != {"kind": "digest-xor-mask", "mask_hex": mask.hex(), "expected_hex": "00" * 32}:
        raise ValueError("unexpected organizer event")
    trials = req["trials"]
    out = []
    if req["experiment_id"] == "rho-w22":
        done, obs = rho_w(trials, step, PD)
        for t, tr in enumerate(trials):
            a, b = done[t]
            ma, mb = msg_of(a), msg_of(b)
            assert ma != mb and (int.from_bytes(digest(ma), "little") ^ int.from_bytes(digest(mb), "little")) & ((1 << W) - 1) == 0
            out.append({"trial": tr["trial"], "message_a_hex": ma.hex(), "message_b_hex": mb.hex(), "observations": obs[t]})
    elif req["experiment_id"] == "proj-w256":
        done = proj_w(trials, step, PD)
        for t, tr in enumerate(trials):
            if done[t] is None:
                out.append({"trial": tr["trial"], "message_a_hex": None, "message_b_hex": None})
            else:
                a, b, s = done[t]
                out.append({"trial": tr["trial"], "message_a_hex": msg_of(a).hex(), "message_b_hex": msg_of(b).hex(), "observations": {"step": s}})
    else:
        raise ValueError("unknown experiment")
    json.dump({"schema_version": 1, "trials": out}, sys.stdout, separators=(",", ":"), sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
