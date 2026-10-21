import hashlib
import json
import sys
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
INV5 = pow(5, -1, P - 1)
MASK256 = (1 << 256) - 1
# Round constants of the deployed Orchard parameter set (zcash/halo2 halo2_poseidon
# 0.2.0, P128Pow5T3: 64 rounds x 3 lanes), canonical hexadecimal field elements.
RC = [
  [0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303, 0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b, 0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8],
  [0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2, 0x073f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3, 0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8],
  [0x270326ee039df19e651e2cfc740628ca634d24fc6e2559f22d8ccbe292efeead, 0x27c6642ac633bc66dc100fe7fcfa54918af895bce012f182a068fc37c182e274, 0x1bdfd8b01401c70ad27f57396989129d710e1fb6ab976a459ca18682e26d7ff9],
  [0x162a14c62f9a89b814b9d6a9c84dd678f4f6fb3f9054d373c832d824261a35ea, 0x2d193e0f76de586b2af6f79e3127feeaac0a1fc71e2cf0c0f79824667b5b6bec, 0x044ca3cc4a85d73b81696ef1104e674f4feff82984990ff85d0bf58dc8a4aa94],
  [0x1cbaf2b371dac6a81d0453416d3e235cb8d9e2d4f314f46f6198785f0cd6b9af, 0x1d5b2777692c205b0e6c49d061b6b5f4293c4ab038fdbbdc343e07610f3fede5, 0x2e9bdbba3dd34bffaa30535bdd749a7e06a9adb0c1e6f962f60e971b8d73b04f],
  [0x2de11886b18011ca8bd5bae36969299fde40fbe26d047b05035a13661f22418b, 0x2e07de1780b8a70d0d5b4a3f1841dcd82ab9395c449be947bc998884ba96a721, 0x0f69f1854d20ca0cbbdb63dbd52dad16250440a99d6b8af3825e4c2bb74925ca],
  [0x2eb1b25417fe17670d135dc639fb09a46ce5113507f96de9816c059422dc705e, 0x115cd0a0643cfb988c24cb44c3fab48aff36c661d26cc42db8b1bdf4953bd82c, 0x26ca293f7b2c462d066d7378b999868bbb57ddf14e0f958ade801612311d04cd],
  [0x17bf1b93c4c7e01a2a830aa162412cd90f160bf9f71e967ff5209d14b24820ca, 0x35b41a7ac4f3c571a24f8456369c85dfe03c0354bd8cfd3805c86f2e7dc293c5, 0x3b1480080523c439435927994849bea964e14d3beb2dddde72ac156af435d09e],
  [0x2cc6810031dc1b0d4950856dc907d57508e286442a2d3eb2271618d874b14c6d, 0x25bdbbeda1bde8c1059618e2afd2ef999e517aa93b78341d91f318c09f0cb566, 0x392a4a8758e06ee8b95f33c25dde8ac02a5ed0a27b61926cc6313487073f7f7b],
  [0x272a55878a08442b9aa6111f4de009485e6a6fd15db89365e7bbcef02eb5866c, 0x2d5b308b0cf02cdfefa13c4e60e26239a6ebba011694dd129b925b3c5b21e0e2, 0x16549fc6af2f3b72dd5d293d72e2e5f244dff42f18b46c56ef38c57c311673ac],
  [0x1b10bb7a82afce39fa69c3a2ad52f76d76398265344203119b7126d9b46860df, 0x0f1e7505ebd91d2fc79c2df7dc98a3bed1b36968ba0405c090d27f6a00b7dfc8, 0x2f313faf0d3f6187537a7497a3b43f46797fd6e3f18eb1caff457756b819bb20],
  [0x3a5cbb6de450b481fa3ca61c0ed15bc55cad11ebf0f7ceb8f0bc3e732ecb26f6, 0x3dab54bc9bef688dd92086e253b439d651baa6e20f892b62865527cbca915982, 0x06dbfb42b979884de280d31670123f744c24b33b410fefd4368045acf2b71ae3],
  [0x068d6b4608aae810c6f039ea1973a63eb8d2de72e3d2c9eca7fc32d22f18b9d3, 0x366ebfafa3ad381c0ee258c9b8fdfccdb868a7d7e1f1f69a2b5dfcc5572555df, 0x39678f65512f1ee404db3024f41d3f567ef66d89d044d022e6bc229e95bc76b1],
  [0x21668f016a8063c0d58b7750a3bc2fe1cf82c25f99dc01a4e534c88fe53d85fe, 0x39d00994a8a5046a1bc749363e98a768e34dea56439fe1954bef429bc5331608, 0x1f9dbdc3f84312636b203bbe12fb3425b163d41605d39f99770c956f60d881b3],
  [0x027745a9cddfad95e5f17b9e0ee0cab6be0bc829fe5e66c69794a9f7c336eab2, 0x1cec0803c504b635788d695c61e932122fa43fe20a45c78d52025657abd8aee0, 0x123523d75e9fabc172077448ef87cc6eed5082c8dbf31365d3872a9559a03a73],
  [0x1723d1452c9cf02df419b848e5d694bf27feba35975ee7e5001779e3a1d357f4, 0x1739d180a16010bdfcc0573d7e61369421c3f776f572836d9dab1ee4dcf96622, 0x2d4e6354da9cc554acce32391794b627fafa96fbeb0ab89370290452042d048d],
  [0x153ee6142e535e334a869553c9d007f88f3bd43f99260621670bcf6f8b485dcd, 0x0c45bfd3a69aaa65635ef7e7a430b486968ad4424af83700d258d2e2b7782172, 0x0adfd53b256a6957f2d56aec831446006897ac0a8ffa5ff10e5633d251f73307],
  [0x315d2ac8ebdbac3c8cd1726b7cbab8ee3f87b28f1c1be4bdac9d36a8b7516d63, 0x1b8472712d02eef4cfaec23d2b16883fc9bb60d1f6959879299ce44ea423d8e1, 0x3c1cd07efda6ff24bd0b70fa2255eb6f367d2c54e36928c9c4a5404198adf70c],
  [0x136052d26bb3d373687f4e51b2e1dcd34a16073f738f7e0cbbe523aef9ab107a, 0x16c96beef6a0a848c1bdd859a1232a1d7b3cfbb873032681676c36c24ef967dd, 0x284b38c57ff65c262ab7fed8f499a9fb012387bab4f1662d067eec7f2d6340c4],
  [0x0c5993d175e81f6639e242198897d17cfc06772c1c0411a6af1dff204c922f86, 0x03bf7a3f7bd043dafcda655d1ba9c8f9f24887ad48e17759bbf53f67b1f87b15, 0x3188fe4ee9f9fafbb0cf999567f00e734c8f9cbe69f0e8279b5cd09e36d8be62],
  [0x171f528ccf6584375a39768c480d61e13af5bf77c1c42652afea99a2ec6c595a, 0x12f4175c4ab45afc196e41859b35ef88812c3286ee7000675a0563b9b8e9f1d5, 0x3a509e155cb7ebfd8f8fdcf800a9ac697e23e1aabe96cfab0e74d4d369118b79],
  [0x10f2a685df4a27c81a89920e2504c3b3984bc8f2e4c1b69e98712c65678cfd30, 0x09e5f49790c8a0e21d8d93d54ab91a0e54573c9333c56321e8a16728cc9d4918, 0x352d69bed80ee3e52bf35705d9f84a3442d17ed6ee0fab7e609a740347cf5fea],
  [0x058ee73ba9f3f293491562faf2b190d3c634debd281b76a63a758af6fa84e0e8, 0x232f99cc911eddd9cd0f1fc55b1a3250092cb92119bc76be621a132510a43904, 0x201beed7b8f3ab8186c22c6c5d4869f0f9efd52ca6bc2961c3b97c1e301bc213],
  [0x1376dce6580030c6a1c9291d58602f5129388842744a1210bf6b3431ba94e9bc, 0x1793199e6fd6ba342b3356c38238f761072ba8b02d92e7226454843c5486d7b3, 0x22de7a7488dcc7359fee9c20c87a67df3c66160dc62aacac06a3f1d3b433311b],
  [0x3514d5e9066bb160df8ff37fe2d8edf8dbe0b77fae77e1d030d6e3fd516b47a8, 0x30cd3006931ad636f919a00dabbf5fa5ff453d6f900f144a19377427137a81c7, 0x253d1a5c5293412741f81a5cf613c8df8f9e4b2cae2ebb515b6a74220692b506],
  [0x035b461c02d79d19a35e9613e7f5fe92851b3a59c990fafc73f666cb86a48e8e, 0x23a9928079d175bd5bc00eedd56b93e092b1283c2d5fccde7cfbf86a3aa04780, 0x13a7785ae134ea92f1594a0763c611abb5e2ea3436eef957f1e4ccd73fa00a82],
  [0x39fce308b7d43c574962ae3c0da17e313889c57863446d88bbf04f5252de4279, 0x1aae18833f8e1d3ac0fdf01662f60d22bef00a08c6ed38d23b57e34489b53fad, 0x1a761ce82400af018b2e80c064fd83ed27c1b3fd8f85d8a855513e033398513f],
  [0x275a03e45adda7c316dd1a87ca22e1ccdcf6af2830a502875244ca749b73e481, 0x2e5a10f08b5ab8bbeb08e47e5feabcf807e561453fc5648b58a253cfb6a95786, 0x1459cb8587208473b84e9c333b2932f1c141a5b6d594bec4e033d82cefe78ce3],
  [0x193ae5921d78b5de7b92ce810e14a40052f9332fbffcfbbd5cec7e7b338fbe1b, 0x3097898a5d0011a489111fb2c4660281374384f4a072820560224be67248e82c, 0x378d97bf8c864ae7571782fd96ce54b41979b2d1c465b4d9549980de862930f5],
  [0x2eb04ea7c01d97ec88136287ce376b08dbc7f5cb4609342137ea32a971d17884, 0x36425347ea03f6412302a1c22e49baec861cbda476804e6cead3726f1af2e7b0, 0x26b72df47408ad42cc996cd85c98a1d83f5b5ca5a19a9701ecd627e59590d09e],
  [0x130180e44e2924db1f05636c610b89aade01212ee4588f8959bece31f0a31e95, 0x219e97737d3979ba73275acaed5f579cdf7793cc89e5b52f9ea8e7bc79263550, 0x3cdb93598a5ca5283461363f81c489a23b0672dd7d42cbb49c12635df251d153],
  [0x0e59e6f332d7ed3720724b927a0ca81c4ad0447045a7c5aa2861ce16f219d5a9, 0x1b064342d51a42753d7369467222697a172cc07b9d33fbf943b0a3fcff2036bd, 0x30b82a998cbd8e8a2f363c55b2882e0b78fa9fb9171221b73eb310228a0e5f6c],
  [0x23e4ab37183acba463df7a76e858a4aa8ad71ea715be0573e46f6d4298740107, 0x2795d5c5fa4280225d33094e0beda75bacfe14640de044f2fca995e2b59914a1, 0x3001ca401e89601cd765f26dd03f4c45a6687c3df16c8fe4c26d909dee8b53c0],
  [0x0072e45cc676b08ef7bf86e89280827fe84b5bebae4e501de7fea6bdf3471380, 0x13de705484874bb5e2abe4c518ce599eb64829e2d40e41bdd0c54ddeb26b86c0, 0x0408a9fcf9d61abf315950f1211defe882bb18e5af1b05bb38915b432a9959a5],
  [0x2780b9e75b55676ebb4e4a1400ccd2c4ae4d23b0b41be9a834070cbee26886a0, 0x3a570d4d7c4e7ac3f80333ec85634ac9dc4d8fbefe24405a9405592098b4056f, 0x0c13cca7cb1f9d2cf347c247fcf09294e2cc1507bebdcc6278d2b247899520b4],
  [0x14f59baa03cd0ca4d2614a197c6b794b0b50bb2eb82df74d2e8c88f7707470e0, 0x307defee925dfb436f546e1704c39c60a51d54ede66167f5be52476e0a16f3be, 0x1960cd511a91e0607a07e7674b5a2621661106836adfe5e7380b67d80473dce3],
  [0x2301ef9c63ea84c5ca2ad0fb56672500b8ee335d88284cbe15aaf1f7712589dd, 0x029a5a47da79a488d10f4cd52be97f6bc86182d1b4246b585e68478c4d6027a9, 0x32d7b16a7f11cc962360d17d890e55cbf97fe46b6a9254282cc4f962eaae2260],
  [0x26703e48c03b81ca18e857a98d498cf7a5f2404cd7b35eb0c0cab915d5363d9f, 0x048682a35b3265bc88ac8d25a24603f1f44388bd6b89221ef691123ae112b928, 0x06b1390441fa7030d72cddc6cf06b50791d6e1715164775e3ab7defcb8d803e2],
  [0x31aa0eeb868c626d1689426dce05fcd843b360f6386a86d7bcd795414a6e2e86, 0x239464f75bf7b6af057abad3764c104b90efd8f41b2078b2ed77f5d576b99cc3, 0x0a64d4c04fd426bda45e19ed813a54aba5cc47c59654b2a7b2cb487307c1cecf],
  [0x21fbbdbb73670734576a4ad259860fb1777c7a921a062e9d1f7315322f658735, 0x31b86f3cf01705d4d9371ca2eb95acf35b86d29463d31564674324003fc52146, 0x2bfde53354377c9105ef1736d09056f613541d65157ee1ce7045f48aa4eb4f6f],
  [0x1233ca936ec24671d558f36e65f8eca7f4d5239c11d0eafa5a13a58d20011e2f, 0x27d452a43ac7dea2c437846d8e0b2b30878058d0234a576f6e70af0a7a924b3a, 0x2699dba82184e413e816ea8da493e0fa6a30641a1c3d87b2a02576b94392f980],
  [0x36c722f0efcc8803c3988baee42e4b10f18584664f8cab49608c6f7a61b56e55, 0x02b3ff48861e339b08b0f2ec89ccaa3785c38899a7b5a8336e49ac170dbb7fcd, 0x0b70d061d58d8a7f60162f4427bc657b6fc3ff4c49eb59ada8c5ae03ad98e405],
  [0x3fc2a13f127f96a4f8753adeb9d7cee2ad3de8be46ed96932e06cc4af33b0a06, 0x0c41a6e48dd23a511bd63434ac8c419f00cb3d621e171d80c12080ac117ee15f, 0x2de8072a6bd86884ed4476537169084e72aaad7e4e75339d9685213e9692f5e1],
  [0x03557a8f7b38a17f9d3496a3d9fe05ecb81cf735cc9c39c00ad01184567b027c, 0x0b5f59552f498735ee976d34282f1a37060f43363d818e5445bcb5ac00826abc, 0x0e2923a5fee7b878fedbb18570dc7300f5d646e57507e5482f2909e17e22b0df],
  [0x1d785005a7a00592c787be97020a7fddcf1cb37c3b032af6f71eed73f15b3326, 0x1ad772c273d9c6df0ba5fedcb8f25bd2a590b88a3b0602940acfbfb223f8f00d, 0x027bd64785fcbd2aa78f3275c278234b810510eb61f0672dc1ce13d60f2f5031],
  [0x20800f441b4a0526ce6f8ffea1031b6de224313469457b8e8337f5e07923a853, 0x3d5ad61d7b65f9386eea2cd49f4312b436cdc8eed662ad37a33d7bed89a4408a, 0x13338bc351fc46dd02c5f91be4dd8e3d1df96cc03ea4b26d3bbbae94cc195284],
  [0x25e52be507c92760b87db1e2af3ea923646c49f9b46cbf19c5271c297852819e, 0x1c492d64c157aaa471096d8b1b983c98a34c83a3485c6b2d5c380ab701b52ea9, 0x0c5b801579992718f4e6c5e7a573f592d43487bc288df682a20c0b3da0da4ca3],
  [0x1090b1b4d2bebe7a68695c0cd7cbf43d584e9e62a7f9554e7ea33c93e40833cf, 0x33e38018a801387a68f5ce5cbed19cad1b218e35ecf2328ee383e1ec3baa8d69, 0x1654af18772b2da5eef8d83d0e876bac5f4a02d28729e3aeb76b0b3d787ee953],
  [0x1678be3cc9c6799344742de88c5ab0d5bb0893870367ec6cef7ce6a013265477, 0x3780bd1e01f34c227ff9c6be546e928adaf1818355b13b4faf5d47893348f766, 0x1e83d6315c9f125b0786018e7cb772675d11e69aa6c0b98ca12380320d7cc1de],
  [0x354afd0a2f9d0b26160b41552f2931c8c486894d76e0c33b1799603e855ce731, 0x00cd6d29f166eadc2d8affa62905c5a560b00dbe1faced078b997ee06be1bff3, 0x1d6219352768e3aedbe0e3d7cdbc66efc60d01973f18305708d0641917082f2c],
  [0x146336e25db5181de48d2370d7d1a142afe3ca1db8d4f529fa08dd9806387577, 0x0005d8e085fd72ee997a21163e2e43df022e54b49c13d907a901d3ce84de0ad4, 0x364e97c7a38932270dd5e61c8a4e86426f8ebc1d2296021a1c36f31341964484],
  [0x01189910671bc16b561c6fff15346878fa97ec80ad307a52d7a00c03d2e0baaa, 0x162a7c80f4d2d12e5229dfaa01231a454c0f7e001df490aa63fd8ac57a95ca8c, 0x2a0d6c09576666bb2604e4afb09f8603caff31b4fda3212432e69efb22f40b96],
  [0x0978e5c51e1e5649e16a4d603d5a808ef444d10d63a74e2cc0a0180f8cbfc0d2, 0x1bdcee3aaca9cd25ebe19bbdce25101105087d903bdacfd103f4460ebc351b6e, 0x1862cccb70b5b885e49479140b1944fd0c947321e0075e3ff61964bf3ade7670],
  [0x1f3e91d863c16922bc26cc883a1987e139ee99c1cc6e5ddac3267da6e94adc50, 0x1af47a48a6016a49ef5c08f8478f663afa661465c656ad990f85b4ac2c367406, 0x3c8ee901956e3d3f009d57338c6935051c3698b0a2e3da100eabcd87e7d01b15],
  [0x1660a8cde7fec55368d0b024f591b520e10ce2b7069f4dbd8b94772189673476, 0x0f6d991929d5e4e71303936334dd11323963c2c1f5586e2f9d8d0f67fdaa79d5, 0x02b9cea1921cd9f6cc625eaaab52b4dc4e7fda770712f3437a433091e1ce2d3a],
  [0x14a323b99b900331214f7c6784acb565d8caf468976f04723797b2d8376043b3, 0x190476b580cb9277ec01ea79642d5760718b7fbc7788af78347fef2c00f0953a, 0x090a3a9d869d2eefa42463d30b442b6f9660902b60087651ff4e7e6fb268dfd7],
  [0x3877a955863675670dbe8fd2270a6795e365001304f9a11ef983387ea0456203, 0x2d894691240fe9535df39a2cc63ddc0a60118c53a218135239c0af0fe01f4a06, 0x21b9c18292bdbc597ef71780201661895914e855eeb44aa11aca9eaf9bba9850],
  [0x2fe76be7cff723e2505a05f2a6ae834c272e1cc6c36a296833f509a74ad9d39b, 0x187aa448f391e3ca929981d7cfce253bd15bff840ddae8a50df9fa97277fa8b4, 0x0b7083ad751707bf007ab3aa3617f422663ccf7b2ffe4b5ef0c66af5ffc73736],
  [0x030ddbb470493f163bc4ca9902c52acb1975b962f6cb8e0b2f9b20f1fbd49791, 0x3130fbaffb5aa82a950b0ab18d3546df8fb8ab9d60ea17b23a1c62ca8fbf2525, 0x337f544707c430f04f74d74bac2ee45715ce2ead2fcd051e43a876180dc382e0],
  [0x349979919015394fac9d91b0930dac757d8e471a9fb95fef26de98a8736d1d11, 0x027cc4efe3fb35dd2305cd7a921ec5f13bf93da6fff31d95ccfcb61831d5c775, 0x037f9f2365954c5b61b71a3698682ad267f1c6b7314764afc3fa2629635d27de],
  [0x1f697cac4d07feb710f1cc6df8b4bcd760414abe362d01c977c5b024848371ae, 0x267a750fe5d7cfbc26e6c851fbd572a63145c478063109d6786add244aa0ef29, 0x0c91feab4a43193a678c9996d9a472c8af285fa82ce4fae5180e2b4d3e756f65],
  [0x1745569a0a3e30142186c3038ea05e697e3b83af4a4ba3ba79c47c573ac410f7, 0x29863d546e7e7c0deca5120778a56711fdff66c6f3b5ffe11e0388522696191f, 0x1148d6ab2bd00192bf06bae49ef853f6a79a03df833994c62f225e6366bfe390],
  [0x02e0e121b0f3dfefe18b1499060da366f745f45d350d41d4f4f6331a8b265d15, 0x0d0aa46e76a6a278b89ef73a40a2b274690401736d44a653078ae6aa151054b7, 0x13943675b04aa986eee545f3fa6d3d08392dde710f1f06db9a4d532c7b6e0958],
  [0x2901ec61942d34aad97a11d63088f5d9c9f2b3257530dafe961fc818dcbb66b5, 0x20204a2105d22e7ef431d54434a3e0cf22ffa2a2af9fa3e3fdf544b963d1fdc7, 0x3a8a628295121d5c5c1e3e9e27a571c3a004abe8e01528c41211b9e2190d6852]
]
# The deployed 3x3 MDS matrix, canonical hexadecimal field elements.
MDS = [
  [0x0ab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63, 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e, 0x07c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d],
  [0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c, 0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e, 0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a],
  [0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4, 0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664, 0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1]
]
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
PRICES = {
  'FADD': 1, 'FSUB': 1, 'FMUL': 1,
  'ADD': 1, 'SUB': 1, 'MUL': 1, 'ADDI': 1, 'SUBI': 1, 'MULI': 1,
  'AND': 1, 'OR': 1, 'XOR': 1,
  'SHL': 1, 'SHR': 1, 'SHLI': 1, 'SHRI': 1,
  'MOV': 1, 'RAND': 1,
  'LOAD': 2, 'STORE': 2, 'LOADC': 2,
  'LOAD_START': 2, 'STORE_START': 2,
  'BLT': 2, 'BGE': 2, 'BEQ': 2, 'BNE': 2,
  'JMP': 1, 'JR': 1, 'HALT': 1,
}
def emit_step(ins, r, r_x, r_u1, r_u2, r_z0, r_z1, r_z2, r_t, c_base):
  """Emit 783-operation (135 + 12*r) step program. Uses r_x as lane 0 (r_u0) throughout."""
  start_len = len(ins)
  r_u0 = r_x
  def pow5(r_in, r_out):
    ins.append(('FMUL', r_out, r_in, r_in))
    ins.append(('FMUL', r_out, r_out, r_out))
    ins.append(('FMUL', r_out, r_out, r_in))
  ins.append(('FADD', r_u1, r_x, c_base + 0))
  ins.append(('FADD', r_u2, r_x, c_base + 1))
  pow5(r_x, r_z0)
  pow5(r_u1, r_z1)
  pow5(r_u2, r_z2)
  for i, r_dst in enumerate((r_u0, r_u1, r_u2)):
    cb = c_base + 2 + 3 * i
    ins.append(('FMUL', r_t, cb + 0, r_z1))
    ins.append(('FADD', r_dst, r_z0, r_t))
    ins.append(('FMUL', r_t, cb + 1, r_z2))
    ins.append(('FADD', r_dst, r_dst, r_t))
    ins.append(('FADD', r_dst, r_dst, cb + 2))
  pow5(r_u0, r_z0)
  pow5(r_u1, r_z1)
  pow5(r_u2, r_z2)
  for i, r_dst in enumerate((r_u0, r_u1, r_u2)):
    cb = c_base + 11 + 2 * i
    ins.append(('FMUL', r_t, cb + 0, r_z1))
    ins.append(('FADD', r_dst, r_z0, r_t))
    ins.append(('FMUL', r_t, cb + 1, r_z2))
    ins.append(('FADD', r_dst, r_dst, r_t))
  for k in range(r):
    cb = c_base + 17 + 5 * k
    ins.append(('FADD', r_u0, r_u0, cb + 0))
    pow5(r_u0, r_z0)
    ins.append(('FMUL', r_t, cb + 1, r_u1))
    ins.append(('FADD', r_u0, r_z0, r_t))
    ins.append(('FMUL', r_t, cb + 2, r_u2))
    ins.append(('FADD', r_u0, r_u0, r_t))
    ins.append(('FMUL', r_t, cb + 3, r_z0))
    ins.append(('FADD', r_u1, r_u1, r_t))
    ins.append(('FMUL', r_t, cb + 4, r_z0))
    ins.append(('FADD', r_u2, r_u2, r_t))
  cb60 = c_base + 17 + 5 * r
  ins.append(('FADD', r_u0, r_u0, cb60 + 0))
  ins.append(('FADD', r_u1, r_u1, cb60 + 1))
  ins.append(('FADD', r_u2, r_u2, cb60 + 2))
  for idx_f in range(3):
    pow5(r_u0, r_z0)
    pow5(r_u1, r_z1)
    pow5(r_u2, r_z2)
    for i, r_dst in enumerate((r_u0, r_u1, r_u2)):
      cb = c_base + 20 + 5 * r + 9 * idx_f + 3 * i
      ins.append(('FMUL', r_t, cb + 0, r_z1))
      ins.append(('FADD', r_dst, r_z0, r_t))
      ins.append(('FMUL', r_t, cb + 1, r_z2))
      ins.append(('FADD', r_dst, r_dst, r_t))
      ins.append(('FADD', r_dst, r_dst, cb + 2))
  pow5(r_u0, r_z0)
  pow5(r_u1, r_z1)
  pow5(r_u2, r_z2)
  cb63 = c_base + 47 + 5 * r
  ins.append(('FMUL', r_t, cb63 + 0, r_z1))
  ins.append(('FADD', r_x, r_z0, r_t))
  ins.append(('FMUL', r_t, cb63 + 1, r_z2))
  ins.append(('FADD', r_x, r_x, r_t))
  assert len(ins) - start_len == 135 + 12 * r
class Program:
  def __init__(self, ins, consts, num_registers, table_words, c_base, step_end_pcs, params):
    self.instructions = ins
    self.constants = consts
    self.num_registers = num_registers
    self.table_words = table_words
    self.c_base = c_base
    self.step_end_pcs = step_end_pcs
    self.params = params
  def memory_bytes(self):
    return (
      4 * len(self.instructions)
      + 32 * self.num_registers
      + 32 * len(self.constants)
      + 32 * self.table_words
      + 32
    )
def build_program(r=54, K=23, VB=142, WG=119, MCAP=28992, Delta=1<<141, S=1000, G=100, GPOS=200):
  base_prog = BASE_R if r == ROUND_COUNT else build_base_constants(r)
  n_step_consts = len(base_prog['flat'])
  v_words = (MCAP * VB + 255) // 256
  g_words = (MCAP * WG + 255) // 256
  t_words = max(v_words + g_words + 1, 5 * r)
  consts = list(base_prog['flat'])
  idx_meta = len(consts)
  consts.extend([
    Delta,
    S,
    G,
    GPOS,
    P - 2,
    INV5,
    D_VEC[0],
    U0_LINE,
    A_LINE,
    V0_LINE,
    B_LINE,
    RC[0][0],
    RC[0][1],
  ])
  r_zero = 0
  r_x = 1
  r_u1, r_u2, r_z0, r_z1, r_z2, r_t = 2, 3, 4, 5, 6, 7
  r_Delta = 8
  r_S = 9
  r_MCAP = 10
  r_gap_lim = 11
  r_mask_vb = 12
  r_mask_wg = 13
  r_vwords = 14
  r_step = 15
  r_count = 16
  r_prev_dp_t = 17
  r_a = 18
  r_rho0 = 19
  r_ret = 20
  r_gap = 21
  c_base = 22
  num_registers = c_base + n_step_consts
  ins = []
  labels = {}
  fixups = []
  step_end_pcs = set()
  def mark(name):
    labels[name] = len(ins)
  def emit(op, a=0, b=0, c=0):
    if op != 'HALT' and isinstance(c, str):
      fixups.append((len(ins), 'c', c))
      ins.append((op, a, b, 0))
    elif op != 'HALT' and isinstance(a, str):
      fixups.append((len(ins), 'a', a))
      ins.append((op, 0, b, c))
    else:
      ins.append((op, a, b, c))
  def emit_pow5_inline(r_in, r_out):
    emit('FMUL', r_out, r_in, r_in)
    emit('FMUL', r_out, r_out, r_out)
    emit('FMUL', r_out, r_out, r_in)
  mark('setup')
  emit('LOADC', r_Delta, r_zero, idx_meta + 0)
  emit('LOADC', r_S, r_zero, idx_meta + 1)
  emit('ADDI', r_MCAP, r_zero, MCAP)
  emit('ADDI', r_t, r_zero, 1)
  emit('SHLI', r_gap_lim, r_t, WG)
  emit('SHLI', r_mask_vb, r_t, VB)
  emit('SUB', r_mask_vb, r_mask_vb, r_t)
  emit('SUB', r_mask_wg, r_gap_lim, r_t)
  emit('ADDI', r_vwords, r_zero, v_words)
  emit('RAND', r_rho0)
  emit('BNE', r_rho0, r_zero, 'setup_rho0_nz')
  emit('ADDI', r_rho0, r_zero, 1)
  mark('setup_rho0_nz')
  emit('RAND', r_x)
  emit('STORE_START', r_x)
  for i in list(range(17)) + list(range(17 + 5 * r, n_step_consts)):
    emit('LOADC', c_base + i, r_zero, i)
  emit('LOADC', r_z0, r_zero, idx_meta + 4)
  emit('MOV', r_u2, r_rho0)
  emit('ADDI', r_ret, r_zero, 'setup_after_inv')
  emit('JMP', 'pow_sub')
  mark('setup_after_inv')
  emit('FMUL', c_base + 0, c_base + 0, r_u1)
  emit('FMUL', c_base + 1, c_base + 1, r_u1)
  emit_pow5_inline(r_u1, r_u2)
  emit_pow5_inline(r_rho0, r_z0)
  emit('FMUL', c_base + 4, c_base + 4, r_u2)
  emit('FMUL', c_base + 7, c_base + 7, r_u2)
  emit('FMUL', c_base + 10, c_base + 10, r_u2)
  emit_pow5_inline(r_z0, r_z1)
  emit_pow5_inline(r_u2, r_z2)
  emit('MOV', r_u1, r_z1)
  emit('MOV', r_u2, r_z2)
  emit('ADDI', r_step, r_zero, 17)
  emit('ADDI', r_count, r_zero, 0)
  emit('ADDI', r_prev_dp_t, r_zero, 17 + 5 * r)
  mark('setup_p_loop')
  emit('LOADC', r_t, r_step, 0)
  emit('FMUL', r_t, r_t, r_u2)
  emit('STORE', r_t, r_count, 0)
  emit_pow5_inline(r_u1, r_z0)
  emit('MOV', r_u1, r_z0)
  emit_pow5_inline(r_u2, r_z0)
  emit('MOV', r_u2, r_z0)
  emit('FMUL', r_ret, r_z1, r_u2)
  emit('FMUL', r_gap, r_u1, r_z2)
  emit('LOADC', r_t, r_step, 1)
  emit('FMUL', r_t, r_t, r_ret)
  emit('STORE', r_t, r_count, 1)
  emit('LOADC', r_t, r_step, 2)
  emit('FMUL', r_t, r_t, r_ret)
  emit('STORE', r_t, r_count, 2)
  emit('LOADC', r_t, r_step, 3)
  emit('FMUL', r_t, r_t, r_gap)
  emit('STORE', r_t, r_count, 3)
  emit('LOADC', r_t, r_step, 4)
  emit('FMUL', r_t, r_t, r_gap)
  emit('STORE', r_t, r_count, 4)
  emit('ADDI', r_step, r_step, 5)
  emit('ADDI', r_count, r_count, 5)
  emit('BLT', r_step, r_prev_dp_t, 'setup_p_loop')
  for i in range(5 * r):
    emit('LOAD', c_base + 17 + i, r_zero, i)
  cb60 = c_base + 17 + 5 * r
  emit('FMUL', cb60 + 0, cb60 + 0, r_u2)
  emit('FMUL', cb60 + 1, cb60 + 1, r_z2)
  emit('FMUL', cb60 + 2, cb60 + 2, r_z2)
  emit_pow5_inline(r_z1, r_ret)
  for idx_f in range(3):
    emit_pow5_inline(r_u2, r_z0)
    emit('MOV', r_u2, r_z0)
    if idx_f == 0:
      emit('FMUL', r_gap, r_ret, r_u2)
    for i in range(3):
      cb = c_base + 20 + 5 * r + 9 * idx_f + 3 * i
      if idx_f == 0:
        emit('FMUL', cb + 0, cb + 0, r_gap)
        emit('FMUL', cb + 1, cb + 1, r_gap)
      emit('FMUL', cb + 2, cb + 2, r_u2)
  emit('ADDI', r_z1, r_zero, t_words)
  emit('ADDI', r_z0, r_zero, 0)
  mark('setup_zero_loop')
  emit('STORE', r_zero, r_z0, 0)
  emit('ADDI', r_z0, r_z0, 1)
  emit('BLT', r_z0, r_z1, 'setup_zero_loop')
  emit('ADDI', r_step, r_zero, 0)
  emit('ADDI', r_count, r_zero, 0)
  emit('ADDI', r_prev_dp_t, r_zero, 0)
  mark('trail_block')
  for j in range(K):
    emit_step(ins, r, r_x, r_u1, r_u2, r_z0, r_z1, r_z2, r_t, c_base)
    step_end_pcs.add(len(ins) - 1)
    emit('BLT', r_x, r_Delta, f'dp_stub_{j}')
    mark(f'after_step_{j}')
  emit('ADDI', r_step, r_step, K)
  emit('BLT', r_step, r_S, 'trail_block')
  emit('HALT', 'no-repeat')
  for j in range(K):
    mark(f'dp_stub_{j}')
    emit('ADDI', r_u1, r_zero, j)
    emit('ADDI', r_ret, r_zero, f'after_step_{j}')
    emit('JMP', 'dp_handler')
  mark('dp_handler')
  emit('ADD', r_u1, r_step, r_u1)
  emit('ADDI', r_u1, r_u1, 1)
  emit('BLT', r_S, r_u1, 'halt_no_repeat_overshoot')
  emit('SUB', r_gap, r_u1, r_prev_dp_t)
  emit('BGE', r_gap, r_gap_lim, 'halt_gap_width')
  emit('ADDI', r_u2, r_zero, 0)
  emit('ADDI', r_z2, r_zero, 0)
  mark('dp_scan_loop')
  emit('BGE', r_u2, r_count, 'dp_scan_done')
  emit('SHRI', r_t, r_z2, 8)
  emit('LOAD', r_z0, r_t, 0)
  emit('LOAD', r_z1, r_t, 1)
  emit('ADDI', r_a, r_zero, 255)
  emit('AND', r_a, r_z2, r_a)
  emit('SHR', r_z0, r_z0, r_a)
  emit('ADDI', r_t, r_zero, 256)
  emit('SUB', r_t, r_t, r_a)
  emit('SHL', r_z1, r_z1, r_t)
  emit('OR', r_z0, r_z0, r_z1)
  emit('AND', r_z0, r_z0, r_mask_vb)
  emit('BEQ', r_z0, r_x, 'dp_match_found')
  emit('ADDI', r_u2, r_u2, 1)
  emit('ADDI', r_z2, r_z2, VB)
  emit('JMP', 'dp_scan_loop')
  mark('dp_scan_done')
  emit('BGE', r_count, r_MCAP, 'halt_table_full')
  emit('SHRI', r_t, r_z2, 8)
  emit('ADDI', r_a, r_zero, 255)
  emit('AND', r_a, r_z2, r_a)
  emit('LOAD', r_z0, r_t, 0)
  emit('SHL', r_z1, r_x, r_a)
  emit('OR', r_z0, r_z0, r_z1)
  emit('STORE', r_z0, r_t, 0)
  emit('ADDI', r_z1, r_zero, 256)
  emit('SUB', r_a, r_z1, r_a)
  emit('LOAD', r_z0, r_t, 1)
  emit('SHR', r_z1, r_x, r_a)
  emit('OR', r_z0, r_z0, r_z1)
  emit('STORE', r_z0, r_t, 1)
  emit('MULI', r_z2, r_count, WG)
  emit('SHRI', r_t, r_z2, 8)
  emit('ADD', r_t, r_t, r_vwords)
  emit('ADDI', r_a, r_zero, 255)
  emit('AND', r_a, r_z2, r_a)
  emit('LOAD', r_z0, r_t, 0)
  emit('SHL', r_z1, r_gap, r_a)
  emit('OR', r_z0, r_z0, r_z1)
  emit('STORE', r_z0, r_t, 0)
  emit('ADDI', r_z1, r_zero, 256)
  emit('SUB', r_a, r_z1, r_a)
  emit('LOAD', r_z0, r_t, 1)
  emit('SHR', r_z1, r_gap, r_a)
  emit('OR', r_z0, r_z0, r_z1)
  emit('STORE', r_z0, r_t, 1)
  emit('ADDI', r_count, r_count, 1)
  emit('MOV', r_prev_dp_t, r_u1)
  emit('JR', r_ret)
  mark('unpack_val_sub')
  emit('MULI', r_z2, r_u2, VB)
  emit('SHRI', r_t, r_z2, 8)
  emit('LOAD', r_z0, r_t, 0)
  emit('LOAD', r_z1, r_t, 1)
  emit('ADDI', r_u1, r_zero, 255)
  emit('AND', r_u1, r_z2, r_u1)
  emit('SHR', r_z0, r_z0, r_u1)
  emit('ADDI', r_t, r_zero, 256)
  emit('SUB', r_t, r_t, r_u1)
  emit('SHL', r_z1, r_z1, r_t)
  emit('OR', r_z0, r_z0, r_z1)
  emit('AND', r_z0, r_z0, r_mask_vb)
  emit('JR', r_ret)
  mark('dp_match_found')
  emit('MULI', r_z2, r_u2, WG)
  emit('SHRI', r_t, r_z2, 8)
  emit('ADD', r_t, r_t, r_vwords)
  emit('LOAD', r_z0, r_t, 0)
  emit('LOAD', r_z1, r_t, 1)
  emit('ADDI', r_a, r_zero, 255)
  emit('AND', r_a, r_z2, r_a)
  emit('SHR', r_z0, r_z0, r_a)
  emit('ADDI', r_t, r_zero, 256)
  emit('SUB', r_t, r_t, r_a)
  emit('SHL', r_z1, r_z1, r_t)
  emit('OR', r_z0, r_z0, r_z1)
  emit('AND', r_S, r_z0, r_mask_wg)
  emit('BEQ', r_u2, r_zero, 'rec_left_from_start')
  emit('SUBI', r_u2, r_u2, 1)
  emit('ADDI', r_ret, r_zero, 'rec_after_left_unpack')
  emit('JMP', 'unpack_val_sub')
  mark('rec_after_left_unpack')
  emit('MOV', r_a, r_z0)
  emit('JMP', 'rec_left_done')
  mark('rec_left_from_start')
  emit('LOAD_START', r_a)
  mark('rec_left_done')
  emit('SUBI', r_u2, r_count, 1)
  emit('ADDI', r_ret, r_zero, 'rec_after_right_unpack')
  emit('JMP', 'unpack_val_sub')
  mark('rec_after_right_unpack')
  emit('MOV', r_x, r_z0)
  emit('BGE', r_gap, r_S, 'rec_order_ok')
  emit('MOV', r_t, r_a)
  emit('MOV', r_a, r_x)
  emit('MOV', r_x, r_t)
  emit('MOV', r_t, r_S)
  emit('MOV', r_S, r_gap)
  emit('MOV', r_gap, r_t)
  mark('rec_order_ok')
  emit('SUB', r_Delta, r_gap, r_S)
  emit('LOADC', r_mask_vb, r_zero, idx_meta + 3)
  emit('LOADC', r_mask_wg, r_zero, idx_meta + 2)
  emit('ADDI', r_step, r_zero, 0)
  mark('rec_pos_loop')
  emit('BGE', r_step, r_Delta, 'rec_pos_done')
  emit('BGE', r_step, r_mask_vb, 'halt_pos_cap')
  emit('ADDI', r_ret, r_zero, 'rec_pos_after_step')
  emit('JMP', 'step_sub')
  mark('rec_pos_after_step')
  emit('ADDI', r_step, r_step, 1)
  emit('JMP', 'rec_pos_loop')
  mark('rec_pos_done')
  emit('MOV', r_vwords, r_x)
  emit('BEQ', r_a, r_vwords, 'halt_start_on_cycle')
  emit('ADDI', r_step, r_zero, 0)
  mark('rec_lock_loop')
  emit('BGE', r_step, r_S, 'halt_lock_cap')
  emit('BGE', r_step, r_mask_wg, 'halt_lock_cap')
  emit('MOV', r_prev_dp_t, r_a)
  emit('MOV', r_gap, r_vwords)
  emit('MOV', r_x, r_a)
  emit('ADDI', r_ret, r_zero, 'rec_lock_after_left')
  emit('JMP', 'step_sub')
  mark('rec_lock_after_left')
  emit('MOV', r_a, r_x)
  emit('MOV', r_x, r_vwords)
  emit('ADDI', r_ret, r_zero, 'rec_lock_after_right')
  emit('JMP', 'step_sub')
  mark('rec_lock_after_right')
  emit('MOV', r_vwords, r_x)
  emit('ADDI', r_step, r_step, 1)
  emit('BEQ', r_a, r_vwords, 'rec_collision_found')
  emit('JMP', 'rec_lock_loop')
  mark('step_sub')
  emit_step(ins, r, r_x, r_u1, r_u2, r_z0, r_z1, r_z2, r_t, c_base)
  step_end_pcs.add(len(ins) - 1)
  emit('JR', r_ret)
  mark('pow_sub')
  emit('ADDI', r_u1, r_zero, 1)
  emit('ADDI', r_z1, r_zero, 0)
  emit('ADDI', r_z2, r_zero, 255)
  mark('pow_sub_loop')
  emit('ADDI', r_t, r_zero, 1)
  emit('AND', r_t, r_z0, r_t)
  emit('BEQ', r_t, r_zero, 'pow_sub_skip')
  emit('FMUL', r_u1, r_u1, r_u2)
  mark('pow_sub_skip')
  emit('FMUL', r_u2, r_u2, r_u2)
  emit('SHRI', r_z0, r_z0, 1)
  emit('ADDI', r_z1, r_z1, 1)
  emit('BLT', r_z1, r_z2, 'pow_sub_loop')
  emit('JR', r_ret)
  mark('rec_collision_found')
  def call_inv5(r_base_in, r_out_acc):
    lbl_ret = f'inv5_ret_{len(ins)}'
    emit('LOADC', r_z0, r_zero, idx_meta + 5)
    emit('MOV', r_u2, r_base_in)
    emit('ADDI', r_ret, r_zero, lbl_ret)
    emit('JMP', 'pow_sub')
    mark(lbl_ret)
    emit('MOV', r_out_acc, r_u1)
  for r_xin, r_m0, r_m1 in ((r_prev_dp_t, r_Delta, r_S), (r_gap, r_MCAP, r_gap_lim)):
    emit('LOADC', r_z0, r_zero, idx_meta + 6)
    emit('FMUL', r_u1, r_xin, r_rho0)
    emit('FSUB', r_u1, r_u1, r_z0)
    call_inv5(r_u1, r_a)
    emit('LOADC', r_z0, r_zero, idx_meta + 7)
    emit('LOADC', r_z1, r_zero, idx_meta + 8)
    emit('FMUL', r_u1, r_z1, r_a)
    emit('FADD', r_u1, r_u1, r_z0)
    call_inv5(r_u1, r_m0)
    emit('LOADC', r_z0, r_zero, idx_meta + 11)
    emit('FSUB', r_m0, r_m0, r_z0)
    emit('LOADC', r_z0, r_zero, idx_meta + 9)
    emit('LOADC', r_z1, r_zero, idx_meta + 10)
    emit('FMUL', r_u1, r_z1, r_a)
    emit('FADD', r_u1, r_u1, r_z0)
    call_inv5(r_u1, r_m1)
    emit('LOADC', r_z0, r_zero, idx_meta + 12)
    emit('FSUB', r_m1, r_m1, r_z0)
  emit('HALT', 'success')
  mark('halt_no_repeat_overshoot')
  emit('HALT', 'no-repeat')
  mark('halt_gap_width')
  emit('HALT', 'gap-width')
  mark('halt_table_full')
  emit('HALT', 'table-full')
  mark('halt_pos_cap')
  emit('HALT', 'positioning-cap')
  mark('halt_start_on_cycle')
  emit('HALT', 'start-on-cycle')
  mark('halt_lock_cap')
  emit('HALT', 'lockstep-cap')
  for idx, pos, name in fixups:
    op, a, b, c = ins[idx]
    if pos == 'c':
      ins[idx] = (op, a, b, labels[name])
    else:
      ins[idx] = (op, labels[name], b, c)
  params = {
    'r': r, 'K': K, 'VB': VB, 'WG': WG, 'MCAP': MCAP,
    'Delta': Delta, 'S': S, 'G': G, 'GPOS': GPOS,
    'out_regs': (r_Delta, r_S, r_MCAP, r_gap_lim),
    'r_rho0': r_rho0,
  }
  return Program(ins, consts, num_registers, t_words, c_base, step_end_pcs, params)
def run_machine(prog: Program, rho0_seed: int, x0_seed: int, truncate_bits: int | None = None):
  reg = [0] * prog.num_registers
  const_mem = list(prog.constants)
  table_mem = [0] * prog.table_words
  start_mem = [0]
  ins = prog.instructions
  step_end_pcs = prog.step_end_pcs
  mask = (1 << truncate_bits) - 1 if truncate_bits is not None else None
  rand_queue = [rho0_seed % P, x0_seed % P]
  if mask is not None:
    rand_queue[1] &= mask
  rho0_eff = rand_queue[0] if rand_queue[0] != 0 else 1
  outscale = scale_step_constants(rho0_eff)[1] if mask is not None else 1
  pc = 0
  ops = 0
  while True:
    op, a, b, c = ins[pc]
    if op == 'FMUL':
      reg[a] = (reg[b] * reg[c]) % P
      ops += 1
      pc += 1
    elif op == 'FADD':
      reg[a] = (reg[b] + reg[c]) % P
      if mask is not None and pc in step_end_pcs:
        reg[a] = ((reg[a] * outscale) % P) & mask
      ops += 1
      pc += 1
    else:
      ops += PRICES[op]
      if op == 'FSUB':
        reg[a] = (reg[b] - reg[c]) % P
        pc += 1
      elif op == 'ADD':
        reg[a] = (reg[b] + reg[c]) & MASK256
        pc += 1
      elif op == 'SUB':
        reg[a] = (reg[b] - reg[c]) & MASK256
        pc += 1
      elif op == 'MUL':
        reg[a] = (reg[b] * reg[c]) & MASK256
        pc += 1
      elif op == 'ADDI':
        reg[a] = (reg[b] + c) & MASK256
        pc += 1
      elif op == 'SUBI':
        reg[a] = (reg[b] - c) & MASK256
        pc += 1
      elif op == 'MULI':
        reg[a] = (reg[b] * c) & MASK256
        pc += 1
      elif op == 'AND':
        reg[a] = reg[b] & reg[c]
        pc += 1
      elif op == 'OR':
        reg[a] = reg[b] | reg[c]
        pc += 1
      elif op == 'SHL':
        reg[a] = (reg[b] << reg[c]) & MASK256 if reg[c] < 256 else 0
        pc += 1
      elif op == 'SHR':
        reg[a] = (reg[b] >> reg[c]) if reg[c] < 256 else 0
        pc += 1
      elif op == 'SHLI':
        reg[a] = (reg[b] << c) & MASK256 if c < 256 else 0
        pc += 1
      elif op == 'SHRI':
        reg[a] = (reg[b] >> c) if c < 256 else 0
        pc += 1
      elif op == 'MOV':
        reg[a] = reg[b]
        pc += 1
      elif op == 'RAND':
        reg[a] = rand_queue.pop(0)
        pc += 1
      elif op == 'LOAD':
        reg[a] = table_mem[reg[b] + c]
        pc += 1
      elif op == 'STORE':
        table_mem[reg[b] + c] = reg[a] & MASK256
        pc += 1
      elif op == 'LOADC':
        reg[a] = const_mem[reg[b] + c]
        pc += 1
      elif op == 'STORE_START':
        start_mem[0] = reg[a]
        pc += 1
      elif op == 'LOAD_START':
        reg[a] = start_mem[0]
        pc += 1
      elif op == 'JMP':
        pc = a
      elif op == 'JR':
        pc = reg[a]
      elif op == 'BEQ':
        pc = c if reg[a] == reg[b] else pc + 1
      elif op == 'BNE':
        pc = c if reg[a] != reg[b] else pc + 1
      elif op == 'BLT':
        pc = c if reg[a] < reg[b] else pc + 1
      elif op == 'BGE':
        pc = c if reg[a] >= reg[b] else pc + 1
      elif op == 'HALT':
        status = a
        pair = None
        if status == 'success':
          r0, r1, r2, r3 = prog.params['out_regs']
          pair = ((reg[r0], reg[r1]), (reg[r2], reg[r3]))
        return status, ops, pair, reg
      else:
        raise ValueError(f"Unknown opcode {op}")
def worst_case_ledger(prog: Program) -> dict:
  p = prog.params
  r = p['r']
  K = p['K']
  MCAP = p['MCAP']
  S = p['S']
  G = p['G']
  GPOS = p['GPOS']
  t_words = prog.table_words
  step_ops = 135 + 12 * r
  pow_p_minus_2_ops = 3 + 255 * 9 + (P - 2).bit_count() + 1
  setup_ops = (
    11
    + 7
    + 98
    + 5 + pow_p_minus_2_ops
    + 19
    + 3 + 39 * r + 10 * r
    + 34
    + 2 + 5 * t_words + 3
  )
  blocks = (S + K - 1) // K
  block_cost = K * (step_ops + 2) + 3
  trail_ops = blocks * block_cost
  dp_ops = 10 * MCAP * (MCAP - 1) + 55 * MCAP
  pow_inv5_ops = 3 + 255 * 9 + INV5.bit_count() + 1
  call_inv5_ops = 6 + pow_inv5_ops
  recon_one_ops = 4 + call_inv5_ops + 2 * (9 + call_inv5_ops)
  recon_ops = 2 * recon_one_ops + 1
  last_ops = (
    12 + 20 * MCAP
    + 70
    + GPOS * (step_ops + 8) + 2
    + 3
    + G * (2 * step_ops + 20)
    + recon_ops
  )
  worst_case_trial = setup_ops + trail_ops + dp_ops + last_ops
  return {
    'setup_ops': setup_ops,
    'trail_ops': trail_ops,
    'dp_ops': dp_ops,
    'last_ops': last_ops,
    'worst_case_trial': worst_case_trial,
  }
def main():
  req = json.loads(sys.stdin.read())
  prog = build_program(r=54, K=23, VB=142, WG=119, MCAP=32, Delta=64, S=69, G=48, GPOS=95)
  ledger_bound = worst_case_ledger(prog)["worst_case_trial"]
  out_trials = []
  for row in req["trials"]:
    idx = row["trial"]
    rho0_s, x0_s = derive_coins(row["seed"])
    st_m, ops_m, pair_m, _ = run_machine(prog, rho0_s, x0_s, truncate_bits=10)
    st_r, pair_r, _, _ = run_reference_trial(
      rho0_s, x0_s, w=10, K=23, WG=119, MCAP=32, Delta=64, S=69, G=48, GPOS=95
    )
    matches_ref = (st_m == st_r and pair_m == pair_r)
    within_ledger = (ops_m <= ledger_bound)
    if not matches_ref or not within_ledger:
      raise RuntimeError(f"Listing verification mismatch at trial {idx}")
    if st_m == "success" and pair_m is not None:
      (nk_a, rho_a), (nk_b, rho_b) = pair_m
      ma = (nk_a.to_bytes(32, "little") + rho_a.to_bytes(32, "little")).hex()
      mb = (nk_b.to_bytes(32, "little") + rho_b.to_bytes(32, "little")).hex()
      if ma == mb:
        ma, mb, st_m = None, None, "start-on-cycle"
    else:
      ma, mb = None, None
    out_trials.append({
      "trial": idx,
      "message_a_hex": ma,
      "message_b_hex": mb,
      "observations": {
        "success": st_m == "success",
        "ops": ops_m,
        "within_ledger": within_ledger,
        "matches_reference": matches_ref,
        "exit_code": EXIT_CODES[st_m],
      }
    })
  sys.stdout.write(json.dumps({"schema_version": 1, "trials": out_trials}) + "\n")
if __name__ == "__main__":
  main()
