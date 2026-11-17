"""LS1, design X: distinguished-point collision search on sha3-256-r19-prefix-v1 with the design-X message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3), proof.md Section 2:
  v_x = u_x (x < 4), v_4 = XOR_(x<4) rotr(u_x, (ROT[4][2] - ROT[x][2]) mod 64);
  m(u) = 128 bytes = lanes 0..15 of the absorbed state: lane x = v_x ^ K_x, lane 10 + x = v_x ^ K_(10+x) (x = 0..4),
  lanes 5..9 all-ones, lane 15 zero; padding gives lane 16 = 0x8000000000000006.  F(u) = SHA3-256-r19(m(u)) XOR PD
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
NR = 19                         # rounds of the target
PLANZ = """
eNrtXd12GzeSvs9T8BHkhEmcC18AaHQ3SNESSLXl1p1MyZCWmeFmlDmtefsBClWoQkvOZHfOnl2dJU9iWc3+AQpVX331g/bvf3u8/XXx7oeff/z5h+/++rfF
u18Wx//8/S/Hu/vFj4vf//a4PyzeLX69ffqd/v7X4+9fj7/eLc6+a98t1L/x0ZPqv/HVzvj4/Xa6b6f068ZapW70g2qUSgeGS/UwGbUNrn04ruJBZeLB+MOb
MOlGj6r38dBzWNkH75Q6jjr9eEMfHdKfTidZiMNNp/0G/gbfD8pMSucL/Gd5vYnfN8p/UmqfD3j14bvuv7teHz5813aL7xcWViPeUduLKFX89vCVz3yCP+30
HkYQP9fp2Wk2Jo/kU/qjpVFOapVHO8T7qcvZ9ONnmaeZrvFw4GNUgJv0HOPL2Xv1nGdpfT6XPnm88NkWycS7q3Stjhrh9w0ebnvPJzdh6OD7LNmkqfFzdtXq
9/kefkzD+qr0mJ9DF6bz8JjSR5p/+tznY/tyT/yMdmuv02paP8zFHgcwfMK/b0xYJpl+BtHE59gsoi/ygjiZTZtl92GBd3h5z2/+xkv9AyrKMQ2/nxktfT42
4Ul1St2mX7o8o4u0dN2kNqAK2qU5XeULN9s47PT3O3G7K7znbRTNVVQHksytLloyfeqnw1xs8OlDVhXrWbV4LCMuVVrxdJv38tKOJ+QuhSpd5GO0hENaxjjG
qW30+yiHTVb/qSwvjDXpQhNVwnpUAaWSMTbNlAeRZGb1dJEt9ZDvT6rAnySXNar6FseOsjqK8b4HwcTlbzs1DbDUzpBqy5VCu+c/WU/FUi8XRVRTdW1fxBCv
b/1yiMu6fgUcbllkezJWUsaCCLh8H4v+aAsWnVf0eIFoofTDkp6xUTpZ/2Gd557uP14iHp43flghOhAK9QqsczJxHjdNiEgBYygotKIzWyGR7iVS0EVxMk87
pSPSPCczcTcFQR6eknzAEqOPIlUY85INDF7oy7IcimpezOR3k9Sv245foonso3y+kAzRpDZdAPX/HOf14ZsA7opTeKECZal/XCBIqnZ6Km6l9/H2foRltGFp
Gn98xR/5pFw3neKpRhd73ZCVSCDSwxcAp6ic3fYpnZee9VVIeyXEjOLFpZmKE8Hl2qykZjfTfFxD17H1qKwCeG36u34iKXws832YruXydCC1aWWfzxSBfoMq
0vjkbKIzewZVu6H7tFnSn5JJ6drpNIBIkzrPmnbmcWybeK+LfN0mrcGXBlWwDWczlTkggBteXGHaHpa5mLJlZRZL/VP01Zu77vk9WFqyLptPnVnw07UicAXx
F3+D1qy+RPGsii+U4B2tsxizP1zgEs8pTPbbE/p2Oj+88INphhH0DncWmMt0DtYfv0cxfYzHvRJK3uj912SVXVbFDTngxp8lNTknsWQvcobPiz/92QtOUHEG
gkO1bPra3xA/uTRbkMM2juUOxpdN4Kq+0yDRkFbyHId5XZZcv/+GVVuWTHj1y7zUPy8SFbOTBMO96vTGJc1FbVJ264iSgZ9DwNsoQie9kb49aWinH4YCIV2m
MD2AXT5xFBTtU7weDDEv19CBpRYf9xSRZa+EGsVbHOlaJBgD+s04s+dIL/O5W3zMrqhaAvPpVXl9zZTocFksVIeOeVmy7s09LX1H6qoPUhPjczcX0llIhAX/
rvdpuJ/7IM6Bi50ielhUDQZ9gOVDeael1i9c9Wsf718u9fukKI0h9poBNYHSdVeWFqjCbbJ60J3tUHyenpBuAcCP4O+bqComA96Yma+acwEVYyhg2/G7FoGP
fNiIqtC8LrLEDTZd9wwXrbP6bAgGbrN6FlYv+eU2Anei5myhcT5dZOhApSYLz+qflxfq+Y/jOrJgUI10D1B3dAw45o4kDX4cOAtyGr9CFLnqM4f42GdaBqDb
bdnZa+AjEv32r1u1/YODDp6Vl/qXePUZ3jKJaWyR+jCiTLNYKdIiHdwt0YpoiRHMp/MmMfWpxFxbcX3yZbfJUk04Rh8HN/zYPeyVUIVo2WfXDKD7+TwuVIkx
lbBmEr0r4JtUNB1DS3513WgpOgzG8Ny2ZjPxwLZYx21b6GK65fESlzYt0xd6tg7jXTLDFK30c/TY+qs4R03qoBPN1cMlBbjNg4v6PcIX3fNBtQ9P6CQT/3va
oFVLi/YvjPmP4up3Z4s0pijvC1C/2fjSXOMa3xXe5JGbhMKnrmx+gIW5VSg0ySVhSqwr8Y/RM6T5R+fkon7sK5LQhlrhECm3iIZf1XNC0M1NvMNqpt+JE162
02uOMI3jTGUnX/jmeVq7DkmGDWea0xlPq0zTh36mZ18ypCRu+JTMMAZFy1vWlZEfOClr/BLDgeVFV7z0AXV9X7wl6vWqy87x0mR9jc9yHxamaK99zYyNpDS8
+LjWKQVT8U8M5Jc4H+CTRKS+dMiHoy7DXfrtU4b9oiOH85JLA48KtrISCneebNbSmutj7dHK8Q1FrcWu7PNT1z9Y+m6bBmYfNpkpALYAI2jABel9E10G4kBo
2FzB/m57gGmAyI+CYcS5H6tMAK7rZxGRp3W7w+TPrpmy4IsNT1WMotQD4kfY73KSZyICWYylz2PeiSRNDkcnxFoOez/8W/myd98vkhvlKF6lzIjH8ZybsFHd
w/QHt0E7jvKG+QM+0Bodh2gTPs25GESoMLSRRD3/fCpY2uhpjQkkuLdl2awyfTgUwhsfAWvWJyzJulBCWKAdcO4YQ/sxx0Y63HZ6gKRW0i2w5yTT57M7tK8k
+zXgSnG9QxqwCD78VStIr34hpzM1z0xJd1+wK8aoSRF7JLmJhSVWm8bc6XANAU3Sawqtnf4z62uFwHGtKWOmXJTrlX6GzJFCWhbt5KyvAwOxLi8/V9luj0pg
/tA8l1TKJmF8/1qsz/HvYB7GbBNxrk317LHIsM1yuYY0w5TlH5ntZboGfe8O9CSoc2TyG/MsYC8Gj9GOdbT/y5KRowE9j2KtaswDfSaKGmO8rItnYJsd+KJh
/NfL4Iu+o8478NlpbZmmEu/ZMEXGgGv45i3/hV2nlJm6YXyq6M8G1wDTX2rVQCnDiwWIeJz0I6fTBtS4O9L3HgaWcHfUlMqXaX3hy28s4NoZ4WA89nRfQkB9
0LM072emapsGiWMe2MNG+CLMwUT9I/9AqSiOmI6f8vo9fcY1lHiddXY6g/FGnXBlzML/GC+V5QAKbNV4kwlGpPrB4c+cXpS2XTK8CAtmu8kRF+dP5hju1Z8K
uwrNxLWGnFn2TQ++ZEXayaquCsr3Cedc5BEJ21pTOJYV2eSNOD/UjBbOCeQDrzvIahewifc8nheMm5JCxd9fuo492t/HKJ/z6Htu0ddcCS64BqFNJS3avZpd
iCFbzrWdwdom2TfJ7rWkPMt7XkuIQ7502eYHKE0FSKGmYsla4ObHJuFhWatsE8nHiBRsxOyxF77sWmRm1+3WUrhmmhzWtX0+98PCfive8lWqlGd8FGv9U8qk
nLeKsUlwgXqxyw3Puld8kAPMnYk1rufGeAv6bLYFy6MsXJLPfcux3MfIRQaYawr8EIfBR4ZcgcspAJ/4xKrgKPDsUi68zrEe2dsAwWX7sJcmcCOyFZZiybZe
m1aeqyc1F0ick1rH61AX9rMV2EB4kW33QDqc/MwnPUEYfsPYlMY63OkwfJSVJk3VFv8kYqJltGutK4MGa/JQ1pOIbl7F8JQ1m6finzBnvGSoZn2/TLhCNpns
pwEuYQFvciXqrCZeyd5znHXfPC9VE/XW+iLzJLdP3fMTpiaeGoq5TTijYiddf8lOG/mv3wx1GavIYN95yqNPPZVfck6fMT7hQgt+uWDldcV8Ci/21/jsPj+7
Xt7Eb6GeEPiaJrxH/w7KvOor77qP3weMq8OG8xbAjUXMEoqH7qc/w8N1Zecmmz6uNaTNvqrT53+xn+H9n46dFtk9uteQ3GP9w4UXSx/X+rJ3i7PFSdgsSxDJ
u5NI5iL5/iSSuUh+OIlkLpLlSSRzkfx4EslcJD+dRDIXyc8nkcxF8v4kkrlIfjmJ5AVVO9HXlzI58deXMjkR2JcyOTHYlzI5UdiXMjlx2JcyOZHYlzL5Qxbr
vn3Y/w8P718Usf78Rif7X5fJicZWMmmsgfTawCUl+Glzt7WP/4ekDkPSiviLM9A0ls9s48GgA65noD1ssD3p9aUBzfI631vqAbQtaLGi2GPq8t1z2lTDU5pv
qJCm/sMyGgvjM3jckWb5ooW0wwSGgrPQpFc2pXC9zRpZyvNKv/LokMoQ8Lz8iJWcMFTr7lNRpk8P0fDQLj7b0mA0HFdWWxBxsREtZAFbvmwepFYB6wPK4mjW
qdDSw6FjuUmWp5Z9h+518wqqkpsr65lb9Y2iZl0vrdjOrk/FnEdFW3mM6vBRZixFN4/nuQOcE8pS4gicEffsXtfaoLioV1CAZzWEelKW1C7VGz3p0hySLGmC
IlWzWXh4H5ePG/x+h4/dopCzqHzp8E/XfQDzsqf09duDxO8XBAlgBWBQGjZSpp0s+jfVJ6tO0OfkBgOL58N1UCdNde6AeIKl7T3+7KiQj0bQBp0NN2jol0VT
T/9dJH1f5xoylpYcPsfh+AB0DGoqjDMe3eEjjPzeJiNV2Dpj6PlOzpf6YQJqN8wzPzfvUODn0iHvc69PajXWsKd3jeNv8RYah0bzTWVcH0/1KI8Vn2eyvAuE
BRwPzd+i96H7OdxaM+B1jrxFuo56kJqQN7k4OA8qt2P67Rblt8cS9ZpREjbOenpulFug9eo9jtPiuPC5nSuuZBVSPX2MLihDEOiPIWiF8y5QOKOjdTNQzn4s
uKV5Pop/V7lnLT9njfLK1/mCX9l1ktxdkU9eYocXLdVg4/E2oFxJL8R94CZw/Y71C/oATJrfHkudFuWZzwulBOrgeJYbQeL/qejfnVDvT0DiD4uAqkumuEyb
nJHIRbzSQBQf0ZSdhKp8PkFpKKqskDA6Uk1SoQn5XEDoDfo9tvYBLvdgyul+ub2JcLeP9uq1wFWbz28JGkOBBjKZgySitFXTsuoT5BgiOABJbCpjYX/Z9A4I
BRkaLVIJgLxl3m6pXDGNAm2V6cVDukCX5fuSPOi5zGoi5F4A2woZ6jJ0sosAAmuChB7FJu3leHYFegxBC7kOV1xSDxCP42iXOXowrsw/39cVqHfoOjR+SffN
nUPIWoFw6X9AVKH099iKO+D4unSyZrI3FFeiYbsFQc2B5aiKfAgCowsQrhe2vY6p1Ufzuip0dbSej+kLh+tUyxVchucoxaFejXmLkq3k8cjyDQVa14IlnpJ/
bw4SU27SIoStUIXWDHGHEkgU1fBFNTtVwrSAvys0ufQSGGRhfP97ZDGKYvX0n2GqE8/7DbdIj/j8I0KGgLSQvjwUdmXWFRtDE2DKaIi9uRJndRWEVSwRxgXR
V3YRv2HLXYCG6FAg54DXkSkEgBJkSQYb7wDfjCssx7JrIRO1OD+EpmTax4xfBjrwpvLuDI3ssMOfLQfyK8AHZol56svUfWrS/bZpSSLbi9BxZIhJcqFooMhh
cJQ1UMymaZwEnR27IsHWbWHJJmT23NG4Q1ERg9KsogyFkEdUFNZb++IiTEpoaIbuFUOlgHpfvhc4fSyQb9g1usp1++JC8vW4GNF/761kgQzVkBPQrkC5YK/H
xK5HwRJPuf83B4mpNOFYpch0r9F7rxGiiikHwxCY9NoZ9sZreNGEK6rjENJWJluZ4YCRTaJlkzeY47OwfZ9N1yHLNGwKSdVzAKthE+BgC8uggNDnTQF5PocE
IYagiNmSkzFTgcYgTc57YmGax0/3CdD9jW8F0hUR9ZK9OWajBFlBQoNNEPaJWTjdp2E2YtFV5Xn6EnjD748Jj7JLOiK7IjY05hxaYUsQ6E6cIDji9+m5+sBQ
x6zMBf3I8ucEyIpZaUgucORANEFJIHlG9j/OWPCRoZHm6yRbc9LVGMn+FDxnkC7PYk57xa4OXMLtXO4ypCnjZH1oOZFyZPae++lTwK0rl24K+15zIsaBqxKQ
eCr9vTlITJVJkXsjlaMcHHlJgi7DOTBfAjpQqT7IwPWxBFB9FbDR+cfi3ftowh4qOqnMMmL5wSNL4ChTQIvFgF0zCyUVP8CuHGYvR8lyKeDKELzM+540QV+o
EwEd55TWlCvDeXVVgM4BX2YzsCc2P9Tl82HevSuBKLAoQ+wosTj9WHKCesaWhIl2zNpcqSFohnLKUcb/Nkn4nCvQxGpHKT+Sk0WoqqMBCowlqyy54oHPc2Ud
HN/UyuvXBbpe5DKVdLlt0Y8kH3ARa8gl6iLvkVl+BUUcIGtwqUdXJ3J8ItSOc5A7vg+5DqQAvZdTcZgrXaIcArNQVs2M4qHofSsC51Pl/81B4s+ZJV5jgLiT
gQCxKsPem9iQY7an0PrY5Fbs5UesDRwKhJWAiE25Y5OC5/ewVa5Ke+8KBPe+BN6aIFoL9iZzlWyKIofEOTTBZh+xIjoKqPB43FuXx9EJyPCFBXIgqyv5EESP
qcruEbLAZDt2DfMcIJWbjGQv0VWIcfNzBVut5KHQhWQ5rwqBIdZVIIwh97EEwPGcLk21J7boi6sogT48b8LKK+dER2RdHIDqHZeBGErNjJULZXqscrLIYrcc
RVzgIhw4dyhcAedCd8UlG/eiXOVCCXzzK1nBZQQWAcvlGsqLCcV7HLKtoPGRXWOVUPEEiaf29TcHiakvyUHARKp6kDmyR1Zdh80w6e0DSfVEAB2kaUJFFtPs
+lgCF1EeoJ+kYpZydVXFz5dcj1Gyko3spHMl4KLKoYCER4YOfq5KaX4B9aVMgFDRQADGucWWz1tjWp0r5GZMzTWvpOeRTXecy9Jkyk6yXSp/jIk1HSXUGS5/
KK7IQyA6MltZpkpoDgwTOzVBJj48B4ocqBrMLe5wx3GfX+UsExeWy2YMDRQVGOgUYPa0w/IGoFkXyrqRq2y5kj5yAqSqdIfS6VJX2g2W36hcY1lOImdb5Sbj
36BfapnfxqJDgeo9dxIomRgRgTYkLgZyDTgeo0QUZL2MSrJ8XR4vdB70QXZIFJZ46vt7c5D4y8JJk2CokDkvVmkRAINW/QeqLAVqkMMZgkhjm2NJ2KwrQsCB
8JoDLctQwBCk2HTTzyDKInnvP1aqKYbqwYjdjG2F/A7qXAm+wMDY+5yLPHKOrAqg5/eBnBmZ1rpiFaE0w4hmFcuBKbOT/Hw476rUfGQlGu9nOPdIJmrZrmFQ
jXBZ2aDrppK9sus6gCwmPWEOkdnqgPcxnLM8MsWEmlGHiZBQXJuhQFyMj1i6rgN9By+/YNcRP3/nhAxGt4XdAcscSiBhnQzISa5Ori+54o5dQ+AmKcdElBMe
B3YB4GLyukj5F9fluVmJXfGIzUfoVVPAr2GdCRJP29feHCS+O1uEWWSxRG5W0SkrMWiLOtaADhMN48Y0xbpoJU0knRb59gNHVFVSb+DIFpM/HdpaJ2yMu0wO
HLEzzeHISEa0IrnFEfw4O/537OIQ9Rcnk6mCXjnGwtRoWTAJ5dqFXDTS86Qd9MRT6d5ZFSQ9XGMmoyoRd6rAHSXRoP6VS6lGCcfBJXLjS1hN31tDJet8kxbX
7w6f2xIW20IzR15HbJsv9Ro/axx1hS7dVD4WYblOjqoipxIGQGncy0ZLoX876VNLV02lB760KGlJt0tYwKXjnBxF36C4PlbqeCHLd13VlVwen66SqqAHAzfG
cq/2m9m/qk+YSKD4boHes8OYpUUH2MIKb1IaJceCAVvA6j4aVDKDsVNImXHRJ+Og+FgqAdrJ4mPdN5FfbG5FF/O8q1pz0ZkqF2DEXZAEg0HnHAikRiOv0mKi
hW9K/UFWVgao4tRArB1mMTl0pwuiS86DW/kMVx6s7FcRaVZqwWszsdaei5ls3KIfaDcjPiaNe8vFflH0njkjjUZsqhY7J3OMK5kjNlWxdcB0nqisBNlXNMxi
/CoN2nFsC3g8ZoLnLRaFRVMA93FpBrm1LmBoZt3this+EwYiomsdNy4R0W7QCeuZk859M3BHi86rkqPldOGx5Cx6ziXQ7gKRLrdUaSugeNrB8vZA8fsFM5TS
Lwtg4LF8CYvsKg9a5dJJeXyJugtjeMydIT7IxFhV/nxkJZXReVLiZXplLPy+m4EhGfsNMaogyo6GawwEoiubv88MlROQwFQ70bQmmakYn+VOGyWZmCizB5FQ
LbUPUQ4V/dhY7jazWlBmGsRIyNh2fL+hbK0RnUOey5+C8WMUWsmrMP4jMnpmxpRQVdx/HOSbCd0sscjMWIlIgebHiTtRE6IEcbCmIEdQ3NRJtTPsCFI2b2WS
7QIVs/clus1y34W89Ur01VdZDMN6y+VvAj2tS4RxkFuDRDOk4QRknEMQTbo6yGi71HAKKJ7eYPH2QPGHBYcv5wAasEH3IJmJAB3y0CJLXfXkAH6N3H5mqh6L
IJStKCszlkRWPYQ1euBqAabgWk4ZroIWIMgd5C23oznZOyGYk5GpzbyJgjfnUHZ+QOOIDOMas+ei54eNa4UMWs8614m27Dk9AA0lK2AWBJ60z69iwCPLK59n
BeNcVe2ZMydQCtvUMwQF1VH2GMVHQnrkc2SOtlRVgiew7wj0QmbIYnPSINdrgPQCdGYvZ70580K26F2yiZEOOQWnKVKwTvTCkH5A1cLwvlDqoTFY1YoHfsM2
WIcgL1Lg+E9GZJAGcO1MFhaDY5xfh6lvHUTbrOYem7aSu0k31bI6JDZRrYE0cMrTSlA87WJ5e6C4XFRh7K7Oq2NEiJuTzcvtA2LnF+f7RX3AKFWVRNFT690s
LDkWhmGhge8fJcuhK/CknVdH7gJy6gvcD8Kx2xTu1zknJ3KCWemvVXk+WMq50gQuo2w0c9U2Gu7ZFcxsrLaxcLeLk4zJmlJSDwHTAA6diTWUpoD5XKS374vt
IYl5ecU7zRRvD3F146VAsJWSOwyJGeGmY3ovg67GPzIjnso2mjbkl4J3Vf0Efs9O6kHUgfqKUSnEL1ucUx7fX7hxkncCOonAYtP3gHpxTWAN78LYSEZHkcpO
grPI6e44zCYQqza536eDxdkEDWCvM8h5JRv6jZP1xoNM34qWibIOBRRP+1jeykcXUPxxwWHYKMMlUVxsq4Q1KM9QGJ9BI7MiTOK9UEaGu3W/SNUyl41DF2Wv
GGnHhYqnEi7XxVqLG2DYGDp8bs+5KuqL6WZMd+Tw7lHmykT4FnADzz0wCF+H2a56g0Fl9K5u2UNQC6Wf6ThzMgdZrIaNQT30lxjJJF3FMEmO1QaaR9nlXG/H
FX1PsshaChBwnw13U4MzOZRwO87jWobReh6Gk97AKsEbH0hv7lXdP0U53T0Xj6u+K8VFbUxHQPrD5wIfz3PA+RvuC6I9ez6F611itC3XDumNHR0XVAwy91GC
7VrVDLROF1VOSmxwynIuoHjayfL2mOJPi6qvNsgNuh2+nGpbhW9eKokAOYNKNM8Z8i6xFTI1CEtTrtIosUvMl9e5rOYdQpzDhJcyQe6zZSf+iUHHzcDNyy0U
ljsr/o704ZPcyjByE6SqmvyYaWVGbTPDqqvPiGzmMRszFazKBnEvt9jc4/cJbMKax33kXB87EVEVDzJHOXDYSTm0X+sOEr1GBrrGnF1AEKyZLIe5dBBA4k6C
uZFOUhNNelRi16aabZDHefsq92iqDfVUZXZp6wm8scsIZsq5bcW7K6tcZvVaoVbmpjVtvA4F7JtQwF1s2K52d/KGdALFMg9bjttZDrblDiaImFKzawHFt76X
xf8/BMXUbN8yk6MOYe50FWHujhlW9VaDNYMIv5OL9pu1CAId7jvrney4hX12Q/W2hKqlxcu3Oij4V9kCvrupCluzUePbB2wQOT4dJBil53gq+Gh6ZxkWQGAc
fdUB7oPm/YouyC3JQVZZnQjvA4FF6Rg3OfYjBk7M8RZzjLpilvzvIO8F45m1pjxyWMtV3mqrtcyx8Xgf5TvDxD4/sUkEcmv8TrAcTtad1fDTsJPkKnL17i3L
zukRc7YlDA+KW5TKZh7Wm/zvUmJuUaQBYJOR2CdKYSvL21T7OO2s3VS8QAlaoh5lAXFdvfXCYqThZIuZk862VaJVreNWn/SCoQKKp90sbwoU/wlStJNg
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
PROG_SHA256 = "4bee0991d049a9166348ff9aff009e6a3c8e91851e823c83c3974133ca74acd2"
NINSTR = 110310
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


SALT = bytes.fromhex("7d2d8f805b71d23261ecbfa4e47c36f2")          # 16 bytes drawn once when this package was generated; prefixed to every trial seed, so no trial is a function of the public seed alone


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
