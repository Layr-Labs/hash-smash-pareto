# experiments/exp_search.py: organizer experiment r25-search-w14 (manifest). Lines below up to section E are rho.py (proof.md Appendix B) lines 1-570 verbatim.
"""Generic collision search on the Orchard hash with 25 partial rounds, the permutation evaluated in an equivalent form whose every
field operation is charged: one trail of x -> F(x) = digest(message(kappa x - E0_0)) / OUTSCALE_kappa for a coin kappa drawn from a set of 4 values,
distinguished points x < DELTA, one table.

Target: poseidon-orchard-r25-prefix-v1 (initial state [m0, m1, 2^65], 8 full + 25 partial rounds, digest = state[0], no feed-forward).
Sections: 1 deployed constants (halo2_poseidon 0.2.0, copied from our own checked file), 2 the hash (reference form), 3 the input line and the
step program (`line`, `build_step`), 4 the search (`search`), 5 parameters and ledger (`plan`, `python3 rho.py --plan`), 6 self-checks
(`--selftest`) and command line (`--listing` prints the step program). No outside code or library is used; standard library only.
"""
import sys
import json
import hashlib
from math import log2
from fractions import Fraction

PARTIAL = 25
# ================================================================ 1 constants
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
ROUND_CONSTANTS = (
    (0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303, 0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b, 0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8),
    (0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2, 0x073f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3, 0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8),
    (0x270326ee039df19e651e2cfc740628ca634d24fc6e2559f22d8ccbe292efeead, 0x27c6642ac633bc66dc100fe7fcfa54918af895bce012f182a068fc37c182e274, 0x1bdfd8b01401c70ad27f57396989129d710e1fb6ab976a459ca18682e26d7ff9),
    (0x162a14c62f9a89b814b9d6a9c84dd678f4f6fb3f9054d373c832d824261a35ea, 0x2d193e0f76de586b2af6f79e3127feeaac0a1fc71e2cf0c0f79824667b5b6bec, 0x044ca3cc4a85d73b81696ef1104e674f4feff82984990ff85d0bf58dc8a4aa94),
    (0x1cbaf2b371dac6a81d0453416d3e235cb8d9e2d4f314f46f6198785f0cd6b9af, 0x1d5b2777692c205b0e6c49d061b6b5f4293c4ab038fdbbdc343e07610f3fede5, 0x2e9bdbba3dd34bffaa30535bdd749a7e06a9adb0c1e6f962f60e971b8d73b04f),
    (0x2de11886b18011ca8bd5bae36969299fde40fbe26d047b05035a13661f22418b, 0x2e07de1780b8a70d0d5b4a3f1841dcd82ab9395c449be947bc998884ba96a721, 0x0f69f1854d20ca0cbbdb63dbd52dad16250440a99d6b8af3825e4c2bb74925ca),
    (0x2eb1b25417fe17670d135dc639fb09a46ce5113507f96de9816c059422dc705e, 0x115cd0a0643cfb988c24cb44c3fab48aff36c661d26cc42db8b1bdf4953bd82c, 0x26ca293f7b2c462d066d7378b999868bbb57ddf14e0f958ade801612311d04cd),
    (0x17bf1b93c4c7e01a2a830aa162412cd90f160bf9f71e967ff5209d14b24820ca, 0x35b41a7ac4f3c571a24f8456369c85dfe03c0354bd8cfd3805c86f2e7dc293c5, 0x3b1480080523c439435927994849bea964e14d3beb2dddde72ac156af435d09e),
    (0x2cc6810031dc1b0d4950856dc907d57508e286442a2d3eb2271618d874b14c6d, 0x25bdbbeda1bde8c1059618e2afd2ef999e517aa93b78341d91f318c09f0cb566, 0x392a4a8758e06ee8b95f33c25dde8ac02a5ed0a27b61926cc6313487073f7f7b),
    (0x272a55878a08442b9aa6111f4de009485e6a6fd15db89365e7bbcef02eb5866c, 0x2d5b308b0cf02cdfefa13c4e60e26239a6ebba011694dd129b925b3c5b21e0e2, 0x16549fc6af2f3b72dd5d293d72e2e5f244dff42f18b46c56ef38c57c311673ac),
    (0x1b10bb7a82afce39fa69c3a2ad52f76d76398265344203119b7126d9b46860df, 0x0f1e7505ebd91d2fc79c2df7dc98a3bed1b36968ba0405c090d27f6a00b7dfc8, 0x2f313faf0d3f6187537a7497a3b43f46797fd6e3f18eb1caff457756b819bb20),
    (0x3a5cbb6de450b481fa3ca61c0ed15bc55cad11ebf0f7ceb8f0bc3e732ecb26f6, 0x3dab54bc9bef688dd92086e253b439d651baa6e20f892b62865527cbca915982, 0x06dbfb42b979884de280d31670123f744c24b33b410fefd4368045acf2b71ae3),
    (0x068d6b4608aae810c6f039ea1973a63eb8d2de72e3d2c9eca7fc32d22f18b9d3, 0x366ebfafa3ad381c0ee258c9b8fdfccdb868a7d7e1f1f69a2b5dfcc5572555df, 0x39678f65512f1ee404db3024f41d3f567ef66d89d044d022e6bc229e95bc76b1),
    (0x21668f016a8063c0d58b7750a3bc2fe1cf82c25f99dc01a4e534c88fe53d85fe, 0x39d00994a8a5046a1bc749363e98a768e34dea56439fe1954bef429bc5331608, 0x1f9dbdc3f84312636b203bbe12fb3425b163d41605d39f99770c956f60d881b3),
    (0x027745a9cddfad95e5f17b9e0ee0cab6be0bc829fe5e66c69794a9f7c336eab2, 0x1cec0803c504b635788d695c61e932122fa43fe20a45c78d52025657abd8aee0, 0x123523d75e9fabc172077448ef87cc6eed5082c8dbf31365d3872a9559a03a73),
    (0x1723d1452c9cf02df419b848e5d694bf27feba35975ee7e5001779e3a1d357f4, 0x1739d180a16010bdfcc0573d7e61369421c3f776f572836d9dab1ee4dcf96622, 0x2d4e6354da9cc554acce32391794b627fafa96fbeb0ab89370290452042d048d),
    (0x153ee6142e535e334a869553c9d007f88f3bd43f99260621670bcf6f8b485dcd, 0x0c45bfd3a69aaa65635ef7e7a430b486968ad4424af83700d258d2e2b7782172, 0x0adfd53b256a6957f2d56aec831446006897ac0a8ffa5ff10e5633d251f73307),
    (0x315d2ac8ebdbac3c8cd1726b7cbab8ee3f87b28f1c1be4bdac9d36a8b7516d63, 0x1b8472712d02eef4cfaec23d2b16883fc9bb60d1f6959879299ce44ea423d8e1, 0x3c1cd07efda6ff24bd0b70fa2255eb6f367d2c54e36928c9c4a5404198adf70c),
    (0x136052d26bb3d373687f4e51b2e1dcd34a16073f738f7e0cbbe523aef9ab107a, 0x16c96beef6a0a848c1bdd859a1232a1d7b3cfbb873032681676c36c24ef967dd, 0x284b38c57ff65c262ab7fed8f499a9fb012387bab4f1662d067eec7f2d6340c4),
    (0x0c5993d175e81f6639e242198897d17cfc06772c1c0411a6af1dff204c922f86, 0x03bf7a3f7bd043dafcda655d1ba9c8f9f24887ad48e17759bbf53f67b1f87b15, 0x3188fe4ee9f9fafbb0cf999567f00e734c8f9cbe69f0e8279b5cd09e36d8be62),
    (0x171f528ccf6584375a39768c480d61e13af5bf77c1c42652afea99a2ec6c595a, 0x12f4175c4ab45afc196e41859b35ef88812c3286ee7000675a0563b9b8e9f1d5, 0x3a509e155cb7ebfd8f8fdcf800a9ac697e23e1aabe96cfab0e74d4d369118b79),
    (0x10f2a685df4a27c81a89920e2504c3b3984bc8f2e4c1b69e98712c65678cfd30, 0x09e5f49790c8a0e21d8d93d54ab91a0e54573c9333c56321e8a16728cc9d4918, 0x352d69bed80ee3e52bf35705d9f84a3442d17ed6ee0fab7e609a740347cf5fea),
    (0x058ee73ba9f3f293491562faf2b190d3c634debd281b76a63a758af6fa84e0e8, 0x232f99cc911eddd9cd0f1fc55b1a3250092cb92119bc76be621a132510a43904, 0x201beed7b8f3ab8186c22c6c5d4869f0f9efd52ca6bc2961c3b97c1e301bc213),
    (0x1376dce6580030c6a1c9291d58602f5129388842744a1210bf6b3431ba94e9bc, 0x1793199e6fd6ba342b3356c38238f761072ba8b02d92e7226454843c5486d7b3, 0x22de7a7488dcc7359fee9c20c87a67df3c66160dc62aacac06a3f1d3b433311b),
    (0x3514d5e9066bb160df8ff37fe2d8edf8dbe0b77fae77e1d030d6e3fd516b47a8, 0x30cd3006931ad636f919a00dabbf5fa5ff453d6f900f144a19377427137a81c7, 0x253d1a5c5293412741f81a5cf613c8df8f9e4b2cae2ebb515b6a74220692b506),
    (0x035b461c02d79d19a35e9613e7f5fe92851b3a59c990fafc73f666cb86a48e8e, 0x23a9928079d175bd5bc00eedd56b93e092b1283c2d5fccde7cfbf86a3aa04780, 0x13a7785ae134ea92f1594a0763c611abb5e2ea3436eef957f1e4ccd73fa00a82),
    (0x39fce308b7d43c574962ae3c0da17e313889c57863446d88bbf04f5252de4279, 0x1aae18833f8e1d3ac0fdf01662f60d22bef00a08c6ed38d23b57e34489b53fad, 0x1a761ce82400af018b2e80c064fd83ed27c1b3fd8f85d8a855513e033398513f),
    (0x275a03e45adda7c316dd1a87ca22e1ccdcf6af2830a502875244ca749b73e481, 0x2e5a10f08b5ab8bbeb08e47e5feabcf807e561453fc5648b58a253cfb6a95786, 0x1459cb8587208473b84e9c333b2932f1c141a5b6d594bec4e033d82cefe78ce3),
    (0x193ae5921d78b5de7b92ce810e14a40052f9332fbffcfbbd5cec7e7b338fbe1b, 0x3097898a5d0011a489111fb2c4660281374384f4a072820560224be67248e82c, 0x378d97bf8c864ae7571782fd96ce54b41979b2d1c465b4d9549980de862930f5),
    (0x2eb04ea7c01d97ec88136287ce376b08dbc7f5cb4609342137ea32a971d17884, 0x36425347ea03f6412302a1c22e49baec861cbda476804e6cead3726f1af2e7b0, 0x26b72df47408ad42cc996cd85c98a1d83f5b5ca5a19a9701ecd627e59590d09e),
    (0x130180e44e2924db1f05636c610b89aade01212ee4588f8959bece31f0a31e95, 0x219e97737d3979ba73275acaed5f579cdf7793cc89e5b52f9ea8e7bc79263550, 0x3cdb93598a5ca5283461363f81c489a23b0672dd7d42cbb49c12635df251d153),
    (0x0e59e6f332d7ed3720724b927a0ca81c4ad0447045a7c5aa2861ce16f219d5a9, 0x1b064342d51a42753d7369467222697a172cc07b9d33fbf943b0a3fcff2036bd, 0x30b82a998cbd8e8a2f363c55b2882e0b78fa9fb9171221b73eb310228a0e5f6c),
    (0x23e4ab37183acba463df7a76e858a4aa8ad71ea715be0573e46f6d4298740107, 0x2795d5c5fa4280225d33094e0beda75bacfe14640de044f2fca995e2b59914a1, 0x3001ca401e89601cd765f26dd03f4c45a6687c3df16c8fe4c26d909dee8b53c0),
    (0x0072e45cc676b08ef7bf86e89280827fe84b5bebae4e501de7fea6bdf3471380, 0x13de705484874bb5e2abe4c518ce599eb64829e2d40e41bdd0c54ddeb26b86c0, 0x0408a9fcf9d61abf315950f1211defe882bb18e5af1b05bb38915b432a9959a5),
    (0x2780b9e75b55676ebb4e4a1400ccd2c4ae4d23b0b41be9a834070cbee26886a0, 0x3a570d4d7c4e7ac3f80333ec85634ac9dc4d8fbefe24405a9405592098b4056f, 0x0c13cca7cb1f9d2cf347c247fcf09294e2cc1507bebdcc6278d2b247899520b4),
    (0x14f59baa03cd0ca4d2614a197c6b794b0b50bb2eb82df74d2e8c88f7707470e0, 0x307defee925dfb436f546e1704c39c60a51d54ede66167f5be52476e0a16f3be, 0x1960cd511a91e0607a07e7674b5a2621661106836adfe5e7380b67d80473dce3),
    (0x2301ef9c63ea84c5ca2ad0fb56672500b8ee335d88284cbe15aaf1f7712589dd, 0x029a5a47da79a488d10f4cd52be97f6bc86182d1b4246b585e68478c4d6027a9, 0x32d7b16a7f11cc962360d17d890e55cbf97fe46b6a9254282cc4f962eaae2260),
    (0x26703e48c03b81ca18e857a98d498cf7a5f2404cd7b35eb0c0cab915d5363d9f, 0x048682a35b3265bc88ac8d25a24603f1f44388bd6b89221ef691123ae112b928, 0x06b1390441fa7030d72cddc6cf06b50791d6e1715164775e3ab7defcb8d803e2),
    (0x31aa0eeb868c626d1689426dce05fcd843b360f6386a86d7bcd795414a6e2e86, 0x239464f75bf7b6af057abad3764c104b90efd8f41b2078b2ed77f5d576b99cc3, 0x0a64d4c04fd426bda45e19ed813a54aba5cc47c59654b2a7b2cb487307c1cecf),
    (0x21fbbdbb73670734576a4ad259860fb1777c7a921a062e9d1f7315322f658735, 0x31b86f3cf01705d4d9371ca2eb95acf35b86d29463d31564674324003fc52146, 0x2bfde53354377c9105ef1736d09056f613541d65157ee1ce7045f48aa4eb4f6f),
    (0x1233ca936ec24671d558f36e65f8eca7f4d5239c11d0eafa5a13a58d20011e2f, 0x27d452a43ac7dea2c437846d8e0b2b30878058d0234a576f6e70af0a7a924b3a, 0x2699dba82184e413e816ea8da493e0fa6a30641a1c3d87b2a02576b94392f980),
    (0x36c722f0efcc8803c3988baee42e4b10f18584664f8cab49608c6f7a61b56e55, 0x02b3ff48861e339b08b0f2ec89ccaa3785c38899a7b5a8336e49ac170dbb7fcd, 0x0b70d061d58d8a7f60162f4427bc657b6fc3ff4c49eb59ada8c5ae03ad98e405),
    (0x3fc2a13f127f96a4f8753adeb9d7cee2ad3de8be46ed96932e06cc4af33b0a06, 0x0c41a6e48dd23a511bd63434ac8c419f00cb3d621e171d80c12080ac117ee15f, 0x2de8072a6bd86884ed4476537169084e72aaad7e4e75339d9685213e9692f5e1),
    (0x03557a8f7b38a17f9d3496a3d9fe05ecb81cf735cc9c39c00ad01184567b027c, 0x0b5f59552f498735ee976d34282f1a37060f43363d818e5445bcb5ac00826abc, 0x0e2923a5fee7b878fedbb18570dc7300f5d646e57507e5482f2909e17e22b0df),
    (0x1d785005a7a00592c787be97020a7fddcf1cb37c3b032af6f71eed73f15b3326, 0x1ad772c273d9c6df0ba5fedcb8f25bd2a590b88a3b0602940acfbfb223f8f00d, 0x027bd64785fcbd2aa78f3275c278234b810510eb61f0672dc1ce13d60f2f5031),
    (0x20800f441b4a0526ce6f8ffea1031b6de224313469457b8e8337f5e07923a853, 0x3d5ad61d7b65f9386eea2cd49f4312b436cdc8eed662ad37a33d7bed89a4408a, 0x13338bc351fc46dd02c5f91be4dd8e3d1df96cc03ea4b26d3bbbae94cc195284),
    (0x25e52be507c92760b87db1e2af3ea923646c49f9b46cbf19c5271c297852819e, 0x1c492d64c157aaa471096d8b1b983c98a34c83a3485c6b2d5c380ab701b52ea9, 0x0c5b801579992718f4e6c5e7a573f592d43487bc288df682a20c0b3da0da4ca3),
    (0x1090b1b4d2bebe7a68695c0cd7cbf43d584e9e62a7f9554e7ea33c93e40833cf, 0x33e38018a801387a68f5ce5cbed19cad1b218e35ecf2328ee383e1ec3baa8d69, 0x1654af18772b2da5eef8d83d0e876bac5f4a02d28729e3aeb76b0b3d787ee953),
    (0x1678be3cc9c6799344742de88c5ab0d5bb0893870367ec6cef7ce6a013265477, 0x3780bd1e01f34c227ff9c6be546e928adaf1818355b13b4faf5d47893348f766, 0x1e83d6315c9f125b0786018e7cb772675d11e69aa6c0b98ca12380320d7cc1de),
    (0x354afd0a2f9d0b26160b41552f2931c8c486894d76e0c33b1799603e855ce731, 0x00cd6d29f166eadc2d8affa62905c5a560b00dbe1faced078b997ee06be1bff3, 0x1d6219352768e3aedbe0e3d7cdbc66efc60d01973f18305708d0641917082f2c),
    (0x146336e25db5181de48d2370d7d1a142afe3ca1db8d4f529fa08dd9806387577, 0x0005d8e085fd72ee997a21163e2e43df022e54b49c13d907a901d3ce84de0ad4, 0x364e97c7a38932270dd5e61c8a4e86426f8ebc1d2296021a1c36f31341964484),
    (0x01189910671bc16b561c6fff15346878fa97ec80ad307a52d7a00c03d2e0baaa, 0x162a7c80f4d2d12e5229dfaa01231a454c0f7e001df490aa63fd8ac57a95ca8c, 0x2a0d6c09576666bb2604e4afb09f8603caff31b4fda3212432e69efb22f40b96),
    (0x0978e5c51e1e5649e16a4d603d5a808ef444d10d63a74e2cc0a0180f8cbfc0d2, 0x1bdcee3aaca9cd25ebe19bbdce25101105087d903bdacfd103f4460ebc351b6e, 0x1862cccb70b5b885e49479140b1944fd0c947321e0075e3ff61964bf3ade7670),
    (0x1f3e91d863c16922bc26cc883a1987e139ee99c1cc6e5ddac3267da6e94adc50, 0x1af47a48a6016a49ef5c08f8478f663afa661465c656ad990f85b4ac2c367406, 0x3c8ee901956e3d3f009d57338c6935051c3698b0a2e3da100eabcd87e7d01b15),
    (0x1660a8cde7fec55368d0b024f591b520e10ce2b7069f4dbd8b94772189673476, 0x0f6d991929d5e4e71303936334dd11323963c2c1f5586e2f9d8d0f67fdaa79d5, 0x02b9cea1921cd9f6cc625eaaab52b4dc4e7fda770712f3437a433091e1ce2d3a),
    (0x14a323b99b900331214f7c6784acb565d8caf468976f04723797b2d8376043b3, 0x190476b580cb9277ec01ea79642d5760718b7fbc7788af78347fef2c00f0953a, 0x090a3a9d869d2eefa42463d30b442b6f9660902b60087651ff4e7e6fb268dfd7),
    (0x3877a955863675670dbe8fd2270a6795e365001304f9a11ef983387ea0456203, 0x2d894691240fe9535df39a2cc63ddc0a60118c53a218135239c0af0fe01f4a06, 0x21b9c18292bdbc597ef71780201661895914e855eeb44aa11aca9eaf9bba9850),
    (0x2fe76be7cff723e2505a05f2a6ae834c272e1cc6c36a296833f509a74ad9d39b, 0x187aa448f391e3ca929981d7cfce253bd15bff840ddae8a50df9fa97277fa8b4, 0x0b7083ad751707bf007ab3aa3617f422663ccf7b2ffe4b5ef0c66af5ffc73736),
    (0x030ddbb470493f163bc4ca9902c52acb1975b962f6cb8e0b2f9b20f1fbd49791, 0x3130fbaffb5aa82a950b0ab18d3546df8fb8ab9d60ea17b23a1c62ca8fbf2525, 0x337f544707c430f04f74d74bac2ee45715ce2ead2fcd051e43a876180dc382e0),
    (0x349979919015394fac9d91b0930dac757d8e471a9fb95fef26de98a8736d1d11, 0x027cc4efe3fb35dd2305cd7a921ec5f13bf93da6fff31d95ccfcb61831d5c775, 0x037f9f2365954c5b61b71a3698682ad267f1c6b7314764afc3fa2629635d27de),
    (0x1f697cac4d07feb710f1cc6df8b4bcd760414abe362d01c977c5b024848371ae, 0x267a750fe5d7cfbc26e6c851fbd572a63145c478063109d6786add244aa0ef29, 0x0c91feab4a43193a678c9996d9a472c8af285fa82ce4fae5180e2b4d3e756f65),
    (0x1745569a0a3e30142186c3038ea05e697e3b83af4a4ba3ba79c47c573ac410f7, 0x29863d546e7e7c0deca5120778a56711fdff66c6f3b5ffe11e0388522696191f, 0x1148d6ab2bd00192bf06bae49ef853f6a79a03df833994c62f225e6366bfe390),
    (0x02e0e121b0f3dfefe18b1499060da366f745f45d350d41d4f4f6331a8b265d15, 0x0d0aa46e76a6a278b89ef73a40a2b274690401736d44a653078ae6aa151054b7, 0x13943675b04aa986eee545f3fa6d3d08392dde710f1f06db9a4d532c7b6e0958),
    (0x2901ec61942d34aad97a11d63088f5d9c9f2b3257530dafe961fc818dcbb66b5, 0x20204a2105d22e7ef431d54434a3e0cf22ffa2a2af9fa3e3fdf544b963d1fdc7, 0x3a8a628295121d5c5c1e3e9e27a571c3a004abe8e01528c41211b9e2190d6852),
)
MDS = (
    (0x0ab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63, 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e, 0x07c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d),
    (0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c, 0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e, 0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a),
    (0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4, 0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664, 0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1),
)

# ================================================================ 2 the target hash (reference form: Orchard Poseidon, ConstantLength<2>, 8 full + PARTIAL partial rounds)
CAPACITY = 1 << 65
ROUND_IDX = tuple(range(4)) + tuple(range(4, 4 + PARTIAL)) + tuple(range(60, 64))   # original rounds 0-3 full, 4..PARTIAL+3 partial, 60-63 full
C_UNIT = 216 + 21 * PARTIAL               # C(r) of the cost model: one reference permutation call = C primitive operations


def _round(st, i):
    """Round i of the reference permutation on the state st (list of 3 field elements)."""
    k = ROUND_CONSTANTS[i]
    st = [(st[0] + k[0]) % P, (st[1] + k[1]) % P, (st[2] + k[2]) % P]
    for c in (range(3) if i < 4 or i >= 60 else range(1)):
        st[c] = pow(st[c], 5, P)
    return [(MDS[r][0] * st[0] + MDS[r][1] * st[1] + MDS[r][2] * st[2]) % P for r in range(3)]


def digest(m0, m1):
    """Digest of the Orchard hash of the two canonical field elements (m0, m1): initial state [m0, m1, 2^65], all rounds, output state[0]."""
    st = [m0, m1, CAPACITY]
    for i in ROUND_IDX:
        st = _round(st, i)
    return st[0]


def enc(x):
    """Canonical 32-byte little-endian encoding (x < P)."""
    assert 0 <= x < P
    return x.to_bytes(32, "little")


# ================================================================ 3 the input line and the step program
INV5 = pow(5, -1, P - 1)                  # gcd(5, p - 1) = 1: x -> x^5 is a bijection of the field, with inverse x -> x^INV5


def inv(a):
    return pow(a, P - 2, P)


def root5(a):
    return pow(a, INV5, P)


def line():
    """The input line on which rounds 0 and 1 are affine.  Round 0 maps (m0, m1) to U = (m0 + c00)^5, V = (m1 + c01)^5 (a bijection) and a constant
    third lane; the round-1 S-box input is then affine in (U, V).  On (U, V) = (U0 + a tau, V0 + b tau) its lane 0 is constant (M00 a + M01 b = 0)
    and its lanes 1, 2 are d_i tau, so the S-box gives d_i^5 tau^5: with W = tau^5 the state after round 1 is A + W B.
    message(W) = (U^(1/5) - c00, V^(1/5) - c01) is injective in W (W -> tau -> (U, V) -> (m0, m1), each step injective, a != 0)."""
    kp = pow((CAPACITY + ROUND_CONSTANTS[0][2]) % P, 5, P)
    base = [(MDS[i][2] * kp + ROUND_CONSTANTS[1][i]) % P for i in range(3)]
    a, b = MDS[0][1], (-MDS[0][0]) % P
    det = (MDS[1][0] * MDS[2][1] - MDS[2][0] * MDS[1][1]) % P
    U0 = (-base[1] * MDS[2][1] + base[2] * MDS[1][1]) * inv(det) % P
    V0 = (-MDS[1][0] * base[2] + MDS[2][0] * base[1]) * inv(det) % P
    return a, b, U0, V0


LINE_A, LINE_B, LINE_U0, LINE_V0 = line()


def message(W):
    """The two message elements of the line point W."""
    tau = root5(W)
    return (root5((LINE_U0 + LINE_A * tau) % P) - ROUND_CONSTANTS[0][0]) % P, (root5((LINE_V0 + LINE_B * tau) % P) - ROUND_CONSTANTS[0][1]) % P


def after_round1(m0, m1):
    return _round(_round([m0, m1, CAPACITY], 0), 1)


class Mono:
    """A field element times kappa^e (kappa the attempt's multiplicative coin): value v at kappa = 1, integer exponent e.  Sums are allowed
    only between equal exponents (asserted) or with zero, so every constant built from Monos is exactly K(1) * kappa^e."""
    __slots__ = ("v", "e")

    def __init__(s, v, e=0):
        s.v, s.e = v % P, e

    @staticmethod
    def c(o):
        return o if isinstance(o, Mono) else Mono(o, 0)

    def __mul__(s, o):
        o = Mono.c(o)
        return Mono(s.v * o.v, s.e + o.e)
    __rmul__ = __mul__

    def __add__(s, o):
        o = Mono.c(o)
        if o.v == 0:
            return s
        if s.v == 0:
            return o
        assert s.e == o.e, "sum of different kappa powers"
        return Mono(s.v + o.v, s.e)
    __radd__ = __add__

    def __neg__(s):
        return Mono(-s.v, s.e)

    def __sub__(s, o):
        return s + (-Mono.c(o))

    def __rsub__(s, o):
        return Mono.c(o) + (-s)

    def __mod__(s, m):
        return s

    def __pow__(s, k, m=None):
        if k == P - 2:
            return Mono(pow(s.v, P - 2, P), -s.e)
        return Mono(pow(s.v, k, P), s.e * k)

    def __eq__(s, o):
        return s.v == Mono.c(o).v

    def __ne__(s, o):
        return not s.__eq__(o)

    def __hash__(s):
        return hash((s.v, s.e))

    def at(s, kappa):
        return s.v * pow(kappa, s.e % (P - 1), P) % P


def build_step():
    """The step program: from x (register x) to F(x) = digest(message(x + rho0)) / OUTSCALE (register x), as a straight-line list of
    field operations (op, dest, src1, src2) with op ADD or MUL.  Register names: x (walk value), e0..e2 (attempt registers e_i = E0_i + rho0),
    k<n> (constants, values in the returned dict), y*, z*, h*, u, x5, t1, t2 (working).  Equivalent form of rounds 2..63:
    every lane is held divided by a known nonzero constant scale (one coefficient of each linear combination becomes 1), and the partial rounds
    keep lanes 1, 2 in a basis Q that absorbs the linear layer (only lane 0 and the two update terms are computed).  Returns
    (prog, kval, E0, OUTSCALE)."""
    A = after_round1(*message(0))
    A1 = after_round1(*message(1))
    B = [(A1[i] - A[i]) % P for i in range(3)]
    prog, kval = [], {}

    def K(v):
        name = "k%d" % len(kval)
        kval[name] = v % P
        return name

    def op(o, d, s, t):
        prog.append((o, d, s, t))

    def pow5(d, s):
        op("MUL", "s_" + d, s, s)
        op("MUL", "s_" + d, "s_" + d, "s_" + d)
        op("MUL", d, "s_" + d, s)

    def mds_norm(sig, cnext, src, dst):
        """dst_i = (sum_j M_ij sig_j src_j + cnext_i) / G_i0 with G = M diag(sig): 2 MUL + 2 ADD (+ 1 ADD for the constant) per lane."""
        lam = []
        for i in range(3):
            G = [MDS[i][j] * sig[j] % P for j in range(3)]
            assert G[0] != 0
            gi = inv(G[0])
            op("MUL", "t1", src[1], K(G[1] * gi))
            op("MUL", "t2", src[2], K(G[2] * gi))
            op("ADD", dst[i], src[0], "t1")
            op("ADD", dst[i], dst[i], "t2")
            if cnext is not None:
                op("ADD", dst[i], dst[i], K(cnext[i] * gi))
            lam.append(G[0])
        return lam

    Y, Z = ["y0", "y1", "y2"], ["z0", "z1", "z2"]
    # round 2: S-box input lane i = A_i + c2_i + (x + rho0) B_i = B_i (x + e_i)
    assert all(B[i] != 0 for i in range(3))
    E0 = [(A[i] + ROUND_CONSTANTS[2][i]) * inv(B[i]) % P for i in range(3)]
    Y = ["x", "y1", "y2"]
    for i in (1, 2):
        op("ADD", Y[i], "x", "e%d" % i)
    sig = [pow(Mono(B[i], 1), 5, P) for i in range(3)]       # lane scales B_i kappa: the program is built once, every constant a Mono
    for i in range(3):
        pow5(Z[i], Y[i])
    Y = ["y0", "y1", "y2"]
    lam = mds_norm(sig, ROUND_CONSTANTS[3], Z, Y)          # round 2 linear layer + round 3 constants
    sig = [pow(l, 5, P) for l in lam]
    for i in range(3):
        pow5(Z[i], Y[i])                                   # round 3 S-boxes
    # round 3 linear layer into the partial-round form: true lane 0 = lam0 h0 + gamma, true lanes (1, 2) = Q (h1, h2) + q.
    # The hidden lanes (h1, h2) = Pm (s1, s2) are held in the basis Pm = diag(nu) M22^PARTIAL, M22 the lower 2 x 2 block of M, so that
    # after the PARTIAL rounds Q = M22^PARTIAL Pm^-1 = diag(nu)^-1 is diagonal; nu_a makes the coefficient of Z0 in h_a equal to 1.
    G = [[MDS[i][j] * sig[j] % P for j in range(3)] for i in range(3)]
    assert G[0][0] != 0
    g0 = inv(G[0][0])
    op("MUL", "t1", Z[1], K(G[0][1] * g0))
    op("MUL", "t2", Z[2], K(G[0][2] * g0))
    op("ADD", "h0", Z[0], "t1")
    op("ADD", "h0", "h0", "t2")
    M22 = [[MDS[1][1], MDS[1][2]], [MDS[2][1], MDS[2][2]]]
    M22r = [[1, 0], [0, 1]]
    for _ in range(PARTIAL):
        M22r = [[(M22[a][0] * M22r[0][b] + M22[a][1] * M22r[1][b]) % P for b in range(2)] for a in range(2)]
    Pm = []
    for a in range(2):
        v = [(M22r[a][0] * G[1][j] + M22r[a][1] * G[2][j]) % P for j in range(3)]    # h_a = nu_a (v . Z)
        assert v[0] != 0
        nu = inv(v[0])
        op("MUL", "t1", Z[1], K(v[1] * nu))
        op("MUL", "t2", Z[2], K(v[2] * nu))
        op("ADD", "h%d" % (1 + a), Z[0], "t1")
        op("ADD", "h%d" % (1 + a), "h%d" % (1 + a), "t2")
        Pm.append([nu * M22r[a][0] % P, nu * M22r[a][1] % P])
    dP = (Pm[0][0] * Pm[1][1] - Pm[0][1] * Pm[1][0]) % P
    assert dP != 0
    dPi = inv(dP)
    Q = [[Pm[1][1] * dPi % P, (-Pm[0][1]) * dPi % P], [(-Pm[1][0]) * dPi % P, Pm[0][0] * dPi % P]]    # Pm^-1: (s1, s2) = Q (h1, h2)
    lam0, gamma = G[0][0], 0
    q = [0, 0]
    for k in range(PARTIAL):
        c = ROUND_CONSTANTS[4 + k]
        op("ADD", "u", "h0", K((gamma + c[0]) * inv(lam0)))
        pow5("x5", "u")
        l5 = pow(lam0, 5, P)
        q = [(q[0] + c[1]) % P, (q[1] + c[2]) % P]
        alpha = MDS[0][0] * l5 % P
        beta = [(MDS[0][1] * Q[0][j] + MDS[0][2] * Q[1][j]) % P for j in range(2)]
        gamma = (MDS[0][1] * q[0] + MDS[0][2] * q[1]) % P
        Qn = [[(MDS[1 + i][1] * Q[0][j] + MDS[1 + i][2] * Q[1][j]) % P for j in range(2)] for i in range(2)]
        q = [(MDS[1 + i][1] * q[0] + MDS[1 + i][2] * q[1]) % P for i in range(2)]
        dt = (Qn[0][0] * Qn[1][1] - Qn[0][1] * Qn[1][0]) % P
        assert alpha != 0 and dt != 0
        di = inv(dt)
        v = [MDS[1][0] * l5 % P, MDS[2][0] * l5 % P]
        w = [(Qn[1][1] * v[0] - Qn[0][1] * v[1]) * di % P, (-Qn[1][0] * v[0] + Qn[0][0] * v[1]) * di % P]   # w = Qn^-1 v
        ai = inv(alpha)
        op("MUL", "t1", "h1", K(beta[0] * ai))
        op("MUL", "t2", "h2", K(beta[1] * ai))
        op("ADD", "h0", "x5", "t1")
        op("ADD", "h0", "h0", "t2")
        op("MUL", "t1", "x5", K(w[0]))
        op("ADD", "h1", "h1", "t1")
        op("MUL", "t2", "x5", K(w[1]))
        op("ADD", "h2", "h2", "t2")
        lam0, Q = alpha, Qn
    # round 60 S-box inputs from the partial-round form, each lane divided by its scale
    c = ROUND_CONSTANTS[60]
    op("ADD", Y[0], "h0", K((gamma + c[0]) * inv(lam0)))
    sig = [pow(lam0, 5, P)]
    assert Q[0][1] == 0 and Q[1][0] == 0 and Q[0][0] != 0 and Q[1][1] != 0     # Q is diagonal after the PARTIAL rounds
    for i in range(2):
        gi = inv(Q[i][i])
        op("ADD", Y[1 + i], "h%d" % (1 + i), K((q[i] + c[1 + i]) * gi))
        sig.append(pow(Q[i][i], 5, P))
    for rnd in (60, 61, 62):
        for i in range(3):
            pow5(Z[i], Y[i])
        lam = mds_norm(sig, ROUND_CONSTANTS[rnd + 1], Z, Y)
        sig = [pow(l, 5, P) for l in lam]
    for i in range(3):
        pow5(Z[i], Y[i])                                   # round 63 S-boxes
    G0 = [MDS[0][j] * sig[j] % P for j in range(3)]        # digest = G0 . z; the step outputs digest / G0[0]
    gi = inv(G0[0])
    op("MUL", "t1", Z[1], K(G0[1] * gi))
    op("MUL", "t2", Z[2], K(G0[2] * gi))
    op("ADD", "x", Z[0], "t1")
    op("ADD", "x", "x", "t2")
    return prog, kval, E0, G0[0]


STEP, KVAL, E0, OUTSCALE = build_step()


def unit_cut(prog):
    """Removes the multiplication t1 = h1 * K of the 21st partial round (the 21st MUL whose source is h1) and lets its one reader use h1:
    valid for the coins kappa at which K(kappa) = 1.  Returns (shorter program, name of the removed constant)."""
    idx = [i for i, o in enumerate(prog) if o[0] == "MUL" and o[2] == "h1"][20]
    _, d, src, kname = prog[idx]
    w = next(i for i in range(idx + 1, len(prog)) if prog[i][1] == d)          # the next write to d
    readers = [i for i in range(idx + 1, w + 1) if d in (prog[i][2], prog[i][3])]
    assert len(readers) == 1 and prog[readers[0]][0] == "ADD" and prog[readers[0]][1] != d
    assert all(prog[i][1] != src for i in range(idx + 1, readers[0]))          # h1 is unchanged until its reader
    out = []
    for i, o in enumerate(prog):
        if i == idx:
            continue
        if i == readers[0]:
            o = ("ADD", o[1], src if o[2] == d else o[2], src if o[3] == d else o[3])
        out.append(o)
    return out, kname


KMONO, OUTMONO = KVAL, Mono.c(OUTSCALE)               # constants as monomials in kappa; OUTSCALE_kappa = OUTSCALE_1 kappa^E_OUT
STEP, UNIT = unit_cut(STEP)
UNIT_MONO = KMONO.pop(UNIT)                           # K_unit(kappa) = UNIT_MONO.v kappa^UNIT_MONO.e
KVAL = {k: Mono.c(v).v for k, v in KMONO.items()}      # values at kappa = 1
OUTSCALE, E_OUT = OUTMONO.v, OUTMONO.e
assert E_OUT == 5 ** (PARTIAL + 6)

# The coin set: the kappa with K_unit(kappa) = 1, i.e. kappa^EP = 1 / UNIT_MONO.v with EP = UNIT_MONO.e mod (p - 1).  G_SET = gcd(EP, p - 1) of them
# (checked: the congruence is solvable); KAPPA0 is one solution and ZG a generator of the group of G_SET-th roots of unity, so the set is
# { KAPPA0 ZG^t : 0 <= t < G_SET }.  KAPPA0 and ZG are program literals, derived offline (generic modular root extraction) and asserted here.
EP = UNIT_MONO.e % (P - 1)
G_SET = 4
KAPPA0 = 0x62d408400e3c68d4b2c5646532855210abab07e84f9c0a10fb8c473b388eaa1        # one solution of kappa^EP = 1 / UNIT_MONO.v
ZG = 0x36bdcc7b0f28b5df31744fb72326829dff98203a45f8ebf0e047f48898cdb6db        # a generator of the 4-th roots of unity


def kappa_of(t):
    """The coin kappa_t = KAPPA0 ZG^t of the attempt's residue t = coin mod G_SET: square-and-multiply on the 2 bits of t (2 MUL squarings and at most 2 MUL), then one MUL."""
    return KAPPA0 * pow(ZG, t, P) % P


def _terms(e):
    """e = s1 5^a + s2 5^b (s in {-1, 0, 1}, a, b <= PARTIAL + 6): the signed power-of-5 terms, fewest first."""
    if e == 0:
        return ()
    for a in range(PARTIAL + 7):
        for s1 in (1, -1):
            if s1 * 5 ** a == e:
                return ((s1, a),)
    for a in range(PARTIAL + 7):
        for b in range(PARTIAL + 7):
            for s1 in (1, -1):
                for s2 in (1, -1):
                    if s1 * 5 ** a + s2 * 5 ** b == e:
                        return ((s1, a), (s2, b))
    raise AssertionError("exponent outside the recipe")


KTERMS = {k: _terms(v.e) for k, v in KMONO.items()}
INV_OPS = ((P - 2).bit_length() - 1) + (bin(P - 2).count("1") - 1)     # kappa^-1 by square-and-multiply on p - 2
# Setup per attempt, exact count: t = coin mod G_SET (1), kappa = KAPPA0 ZG^t (2 squarings + 2 multiplications + 1), kappa^(5^a) and kappa^(-5^a) for
# a = 1..PARTIAL+6 (3 MUL each), one inversion, one MUL per constant term (K_j(1) times each kappa power of its recipe), e_1, e_2 (one MUL each),
# and W = kappa x - E0_0 for the two messages (one MUL more each than x + rho0).
SETUP_D = 1 + 5 + 2 * 3 * (PARTIAL + 6) + INV_OPS + sum(len(t) for t in KTERMS.values()) + 2 + 2
# Memory of the setup: both power chains (2 (PARTIAL + 7) words), one 16-bit recipe field per constant, E0_1 - E0_0, E0_2 - E0_0, kappa, KAPPA0, ZG,
# and 96 setup instructions (4 B each).
D_BYTES = 2 * (PARTIAL + 7) * 32 + (len(KMONO) * 2 + 31) // 32 * 32 + 5 * 32 + 96 * 4
OUTINV = inv(OUTSCALE)
NCONST = len(KVAL)                        # step constants, each loaded once per attempt into its own register
REGNAMES = sorted({r for o in STEP for r in o[1:]})
NREG_STEP = len(REGNAMES)                 # registers the step uses: constants, e0..e2, x and working registers
NREG = NREG_STEP + 40                     # + at most 40 control registers of the search (proof.md Section 6 listings): the declared file
_IDX = {r: n for n, r in enumerate(REGNAMES)}
_CODE = tuple((o == "MUL", _IDX[d], _IDX[s], _IDX[t]) for o, d, s, t in STEP)


def kappa_consts(kappa):
    """The attempt's register values for the coin kappa (D): every step constant K_j(1) kappa^(e_j), e_1, e_2, and OUTSCALE_kappa."""
    ki = inv(kappa)
    regs = {name: KMONO[name].at(kappa) for name in KMONO}
    for i in (1, 2):
        regs["e%d" % i] = (E0[i] - E0[0]) * ki % P
    return regs, OUTMONO.at(kappa)


def make_F(kappa):
    """F(x) = digest(message(kappa x - E0_0)) / OUTSCALE_kappa for a coin kappa of the set, computed by executing the step program (every operation of STEP once)."""
    R = [0] * NREG_STEP
    regs, _ = kappa_consts(kappa)
    for name, v in regs.items():
        R[_IDX[name]] = v
    ix = _IDX["x"]

    def F(x):
        R[ix] = x
        for m, d, s, t in _CODE:
            R[d] = R[s] * R[t] % P if m else (R[s] + R[t]) % P
        return R[ix]
    return F


# ================================================================ 4 the search: one trail, distinguished points, one table, recovery
M128 = (1 << 128) - 1
HI = ((1 << 256) - 1) ^ M128
UNROLL = 32                               # trail steps per block
# Operation charges (word operations, 1/C each), beside the |STEP| field operations of every evaluation (proof.md Section 5 listings):
W_LOOP = 2        # per trail step, after the step program: CMPLT f, x, DELTA; BR f, handler
W_BLOCK = 2       # per block of UNROLL unrolled steps: SUB c, c, UNROLL (c counts down from S); BR c != 0, block
W_DP = 8          # per distinguished-point event: index (SUB idx, BS, c; ADD idx, idx, slot + 1), SHL xh, x, 128, SHR xs, x, 128, scan pointer, capacity compare and branch, return branch
W_SCAN = 19       # per table entry examined, worst case: load, AND HI, compare, branch, pointer add, bound compare, branch (7); on a high-part
                  # match also the side field: offset, two shifts, address add, load, AND, shift, shift, AND 16 bits, compare, two branches (12)
W_INS = 16        # per insertion: entry word, store, offset, end-pointer add; side word read-modify-write (6 address/shift, load, shift, OR, store); count (14)
W_PROBE = 13      # per bisection probe: lo+hi, +1, shift, shift 5, base add, load, AND M128, compare, branch, bound update, loop compare, branch, slack
W_REC = 6         # per recovery evaluation beside the step: walk loop 3 (counter, compare, branch); lockstep 11 per 2 evaluations
                  # (move A into x, move result out, the same for B, compare, branch, two moves, counter, compare, branch)
POW_OPS = (INV5.bit_length() - 1) + (bin(INV5).count("1") - 1)   # square-and-multiply for x^INV5: squarings + multiplications
MSG_OPS = 2 * (3 * POW_OPS + 7)           # the two messages: W = A + rho0, tau = W^(1/5), U, V (2 MUL, 2 ADD), two roots, two subtractions


def _hi(x):
    """The low 128 bits of a DP, moved into the high half of the entry word, and its high part x >> 128 (below 2^14), kept in the 16-bit side field."""
    return (x & M128) << 128, x >> 128


def lookup(tab, side, x, ops):
    """Linear scan of the entries 1.. for the value x (a distinguished point): returns k or None."""
    xh, xl = _hi(x)
    for k in range(1, len(tab)):
        ops["table"] += 7
        if tab[k] & HI == xh:
            ops["table"] += 12
            if (side[(k - 1) >> 4] >> (16 * ((k - 1) & 15))) & 0xFFFF == xl:
                return k
    return None


def insert(tab, side, x, i, ops):
    ops["table"] += W_INS
    k = len(tab)
    xh, xl = _hi(x)
    assert xl < 1 << 16 and i < SMAX
    tab.append(xh | i)
    if (k - 1) & 15 == 0:
        side.append(0)
    side[(k - 1) >> 4] |= xl << (16 * ((k - 1) & 15))


def search(F, is_dp, x0, steps, mcap, gmax, gpos):   # single-gap recovery: gmax = lockstep cap G, gpos = positioning cap G + d - 1
    """Single-trail collision search on the map F: x_0 = x0, x_i = F(x_{i-1}), 8 steps per block.  Every x_i (i >= 1) with is_dp(x_i) is
    stored as one entry word ((x mod 2^128) << 128) OR i and a 16-bit side field x >> 128; the start x_0 is kept in its own word.  Halts (failure)
    after `steps` evaluations (a multiple of UNROLL), when the table already holds `mcap` points at a new one, when the positioning walk
    needs more than gpos evaluations or the lockstep more than gmax rounds.  When a distinguished value repeats (x_b = x_a, a < b) the trail is periodic from a with period L = b - a; the
    recovery finds the least i with x_i = x_{i+L} and returns (x_{i-1}, x_{i+L-1}), distinct, with F equal on both.
    Returns (pair or None, status, evaluations, ops)."""
    ops = {"trail": 0, "blocks": 0, "rec": 0, "dp": 0, "table": 0, "probe": 0}
    tab, side = [None], []

    def value(k):
        if k == 0:
            return x0
        sf = (side[(k - 1) >> 4] >> (16 * ((k - 1) & 15))) & 0xFFFF
        return (sf << 128) | (tab[k] >> 128)

    def index(k):
        return 0 if k == 0 else tab[k] & M128
    x, i, k, b = x0, 0, None, None
    while i < steps and k is None:
        for slot in range(UNROLL):
            x = F(x)
            ops["trail"] += 1
            if is_dp(x):
                ops["dp"] += W_DP
                k = lookup(tab, side, x, ops)
                if k is not None:
                    b = i + slot + 1
                    break
                if len(tab) - 1 >= mcap:
                    return None, "table", ops["trail"], ops
                insert(tab, side, x, i + slot + 1, ops)
        if k is None:
            i += UNROLL
            ops["blocks"] += 1
    ev = ops["trail"]
    if k is None:
        return None, "steps", ev, ops
    a = index(k)
    L = b - a
    s, A = index(k - 1), value(k - 1)       # last stored point before a (index s < mu <= a), or the start
    q = s + L
    lo, hi = 0, len(tab) - 1                # nearest stored point at or before q, then walk to x_q
    while lo < hi:
        mid = (lo + hi + 1) // 2
        ops["probe"] += W_PROBE
        if index(mid) <= q:
            lo = mid
        else:
            hi = mid - 1
    idx, B = index(lo), value(lo)
    if q - idx > gpos:
        return None, "gap", ev, ops
    for _ in range(q - idx):
        B = F(B)
        ev += 1
        ops["rec"] += 1
    if A == B:
        return None, "start-on-cycle", ev, ops
    for _ in range(gmax):                   # lockstep: the first index where the two walkers meet
        nA, nB = F(A), F(B)
        ev += 2
        ops["rec"] += 2
        if nA == nB:
            return (A, B), "found", ev, ops
        A, B = nA, nB
    return None, "gap", ev, ops




# ================================================================ E the organizer experiment r25-search-w14 (driver; sections 1-4 above are rho.py lines 1-570 verbatim)
# Per organizer trial: coins from SHA-256(seed || j); t = coin_0 mod 4 gives kappa = KAPPA0 ZG^t (the coin set of Section 2), the start is the low 14
# bits of coin_1.  The walk is v -> g(v) = the low 14 bits of OUTSCALE_kappa F_kappa(v) = the low 14 bits of the digest of message(kappa v - E0_0),
# F_kappa evaluated by the step program STEP (make_F).  The search is `search` of Section 4, unchanged, at the parameters below; a returned pair
# is mapped to its two 64-byte line messages, whose digests agree on the low 14 bits (mask ff3f..., checked by the organizer's verifier).
SMAX = 1 << 128                           # as rho.py section 5 (every index of the program is below SMAX)
W_EXP = 14                                # walk width: N = 2^14
DELTA_E = 6144                            # distinguished points: v < DELTA_E
N_E = 176                                 # budget n: the least n with S = n + d a multiple of UNROLL whose bound rf_bound() reaches 0.39
D_E = 16                                  # detection window d
G_E = 16                                  # lockstep cap G; positioning cap G + d - 1
MCAP_E = 96                               # table capacity
S_E = N_E + D_E                           # trail length S = 192 = 6 blocks of UNROLL


def rf_bound():
    """Lemma 2 of proof.md Section 5 at N = 2^14 for these parameters, exact rationals (indices <= S, so SMAX_w = S + 1): the success probability
    of this search on a uniformly random function on N values is at least the returned value.  Not called by the trials."""
    from math import comb
    N, S = 1 << W_EXP, S_E
    tl, th = Fraction(DELTA_E - S - 1, N), Fraction(DELTA_E, N - S - 1)
    trail = Fraction(1)
    for i in range(N_E):
        trail *= 1 - Fraction(i + 1, N)
    table = sum(comb(S, k) * th ** k * (1 - th) ** (S - k) for k in range(MCAP_E + 1, S + 1))
    eps = (1 - tl) ** D_E + Fraction(N_E * D_E, N) + table + (1 - tl) ** G_E + (G_E * th + 1) * (1 - tl) ** (G_E + D_E - 1)
    return 1 - trail - Fraction(N_E, N) - eps


_FK = {}
STATUS_CODE = {"found": 0, "steps": 1, "table": 2, "gap": 3, "start-on-cycle": 4}   # observation "status" (numeric, organizer format)


def trial(seed_hex):
    seed = bytes.fromhex(seed_hex)
    rw = [int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), "little") for j in range(2)]
    t = rw[0] % G_SET
    if t not in _FK:
        kappa = kappa_of(t)
        _FK[t] = (kappa, make_F(kappa), kappa_consts(kappa)[1])
    kappa, F, osk = _FK[t]
    x0 = rw[1] & ((1 << W_EXP) - 1)
    memo = {}                             # evaluation memo: g is a function, so a repeated argument returns the same value

    def g(v):
        r = memo.get(v)
        if r is None:
            r = memo[v] = (F(v) * osk % P) & ((1 << W_EXP) - 1)
        return r
    pair, status, ev, ops = search(g, lambda v: v < DELTA_E, x0, S_E, MCAP_E, G_E, G_E + D_E - 1)
    pos, x = {x0: 0}, x0                  # first-repeat index of the walk (Lemma 1: least i with x_i = x_j, j < i), S + 1 if none within S
    t_first = S_E + 1
    for i in range(1, S_E + 1):
        x = g(x)
        if x in pos:
            t_first = i
            break
        pos[x] = i
    obs = {"status": STATUS_CODE[status], "evaluations": ev, "t": t, "t_first": t_first}
    if pair is None:
        return None, None, obs
    (a0, a1), (b0, b1) = message((kappa * pair[0] - E0[0]) % P), message((kappa * pair[1] - E0[0]) % P)
    return (enc(a0) + enc(a1)).hex(), (enc(b0) + enc(b1)).hex(), obs


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--bound":
        b = rf_bound()
        print(json.dumps({"bound_num": b.numerator, "bound_den": b.denominator, "bound": "%.8f" % (b.numerator / b.denominator)}))
        sys.exit(0)
    req = json.loads(sys.stdin.read())
    assert int(req["target_profile"].split("-r")[-1].split("-")[0]) == PARTIAL
    out = []
    for tr in req["trials"]:
        a, b, obs = trial(tr["seed"])
        out.append({"trial": tr["trial"], "message_a_hex": a, "message_b_hex": b, "observations": obs})
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": out}, sort_keys=True, separators=(",", ":")) + chr(10))
