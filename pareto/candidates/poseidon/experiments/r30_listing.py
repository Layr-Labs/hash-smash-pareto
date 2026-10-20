"""r30_listing.py - organizer experiment (python-message-pairs-v1) for poseidon-orchard-r30-prefix-v1.
For each trial seed: coins from SHA-256(seed), the complete search listing of proof Section 3 (machine.py, unchanged
except one MUL by OUTSCALE and one AND with the width mask after each step-program instance, so the walk runs on the
low 10 bits of the digest), executed by the counting interpreter on the real r = 30 step program. A successful
attempt returns two distinct canonical messages whose digests agree on the low 10 bits (a mask event, not a
collision); a failed attempt returns nulls. Observations: the counted cost and the worst-case bound of the listing."""
import sys, json, hashlib
EMBEDDED = {"round_constants": [["0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303", "0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b", "0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8"], ["0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2", "0x73f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3", "0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8"], ["0x270326ee039df19e651e2cfc740628ca634d24fc6e2559f22d8ccbe292efeead", "0x27c6642ac633bc66dc100fe7fcfa54918af895bce012f182a068fc37c182e274", "0x1bdfd8b01401c70ad27f57396989129d710e1fb6ab976a459ca18682e26d7ff9"], ["0x162a14c62f9a89b814b9d6a9c84dd678f4f6fb3f9054d373c832d824261a35ea", "0x2d193e0f76de586b2af6f79e3127feeaac0a1fc71e2cf0c0f79824667b5b6bec", "0x44ca3cc4a85d73b81696ef1104e674f4feff82984990ff85d0bf58dc8a4aa94"], ["0x1cbaf2b371dac6a81d0453416d3e235cb8d9e2d4f314f46f6198785f0cd6b9af", "0x1d5b2777692c205b0e6c49d061b6b5f4293c4ab038fdbbdc343e07610f3fede5", "0x2e9bdbba3dd34bffaa30535bdd749a7e06a9adb0c1e6f962f60e971b8d73b04f"], ["0x2de11886b18011ca8bd5bae36969299fde40fbe26d047b05035a13661f22418b", "0x2e07de1780b8a70d0d5b4a3f1841dcd82ab9395c449be947bc998884ba96a721", "0xf69f1854d20ca0cbbdb63dbd52dad16250440a99d6b8af3825e4c2bb74925ca"], ["0x2eb1b25417fe17670d135dc639fb09a46ce5113507f96de9816c059422dc705e", "0x115cd0a0643cfb988c24cb44c3fab48aff36c661d26cc42db8b1bdf4953bd82c", "0x26ca293f7b2c462d066d7378b999868bbb57ddf14e0f958ade801612311d04cd"], ["0x17bf1b93c4c7e01a2a830aa162412cd90f160bf9f71e967ff5209d14b24820ca", "0x35b41a7ac4f3c571a24f8456369c85dfe03c0354bd8cfd3805c86f2e7dc293c5", "0x3b1480080523c439435927994849bea964e14d3beb2dddde72ac156af435d09e"], ["0x2cc6810031dc1b0d4950856dc907d57508e286442a2d3eb2271618d874b14c6d", "0x25bdbbeda1bde8c1059618e2afd2ef999e517aa93b78341d91f318c09f0cb566", "0x392a4a8758e06ee8b95f33c25dde8ac02a5ed0a27b61926cc6313487073f7f7b"], ["0x272a55878a08442b9aa6111f4de009485e6a6fd15db89365e7bbcef02eb5866c", "0x2d5b308b0cf02cdfefa13c4e60e26239a6ebba011694dd129b925b3c5b21e0e2", "0x16549fc6af2f3b72dd5d293d72e2e5f244dff42f18b46c56ef38c57c311673ac"], ["0x1b10bb7a82afce39fa69c3a2ad52f76d76398265344203119b7126d9b46860df", "0xf1e7505ebd91d2fc79c2df7dc98a3bed1b36968ba0405c090d27f6a00b7dfc8", "0x2f313faf0d3f6187537a7497a3b43f46797fd6e3f18eb1caff457756b819bb20"], ["0x3a5cbb6de450b481fa3ca61c0ed15bc55cad11ebf0f7ceb8f0bc3e732ecb26f6", "0x3dab54bc9bef688dd92086e253b439d651baa6e20f892b62865527cbca915982", "0x6dbfb42b979884de280d31670123f744c24b33b410fefd4368045acf2b71ae3"], ["0x68d6b4608aae810c6f039ea1973a63eb8d2de72e3d2c9eca7fc32d22f18b9d3", "0x366ebfafa3ad381c0ee258c9b8fdfccdb868a7d7e1f1f69a2b5dfcc5572555df", "0x39678f65512f1ee404db3024f41d3f567ef66d89d044d022e6bc229e95bc76b1"], ["0x21668f016a8063c0d58b7750a3bc2fe1cf82c25f99dc01a4e534c88fe53d85fe", "0x39d00994a8a5046a1bc749363e98a768e34dea56439fe1954bef429bc5331608", "0x1f9dbdc3f84312636b203bbe12fb3425b163d41605d39f99770c956f60d881b3"], ["0x27745a9cddfad95e5f17b9e0ee0cab6be0bc829fe5e66c69794a9f7c336eab2", "0x1cec0803c504b635788d695c61e932122fa43fe20a45c78d52025657abd8aee0", "0x123523d75e9fabc172077448ef87cc6eed5082c8dbf31365d3872a9559a03a73"], ["0x1723d1452c9cf02df419b848e5d694bf27feba35975ee7e5001779e3a1d357f4", "0x1739d180a16010bdfcc0573d7e61369421c3f776f572836d9dab1ee4dcf96622", "0x2d4e6354da9cc554acce32391794b627fafa96fbeb0ab89370290452042d048d"], ["0x153ee6142e535e334a869553c9d007f88f3bd43f99260621670bcf6f8b485dcd", "0xc45bfd3a69aaa65635ef7e7a430b486968ad4424af83700d258d2e2b7782172", "0xadfd53b256a6957f2d56aec831446006897ac0a8ffa5ff10e5633d251f73307"], ["0x315d2ac8ebdbac3c8cd1726b7cbab8ee3f87b28f1c1be4bdac9d36a8b7516d63", "0x1b8472712d02eef4cfaec23d2b16883fc9bb60d1f6959879299ce44ea423d8e1", "0x3c1cd07efda6ff24bd0b70fa2255eb6f367d2c54e36928c9c4a5404198adf70c"], ["0x136052d26bb3d373687f4e51b2e1dcd34a16073f738f7e0cbbe523aef9ab107a", "0x16c96beef6a0a848c1bdd859a1232a1d7b3cfbb873032681676c36c24ef967dd", "0x284b38c57ff65c262ab7fed8f499a9fb012387bab4f1662d067eec7f2d6340c4"], ["0xc5993d175e81f6639e242198897d17cfc06772c1c0411a6af1dff204c922f86", "0x3bf7a3f7bd043dafcda655d1ba9c8f9f24887ad48e17759bbf53f67b1f87b15", "0x3188fe4ee9f9fafbb0cf999567f00e734c8f9cbe69f0e8279b5cd09e36d8be62"], ["0x171f528ccf6584375a39768c480d61e13af5bf77c1c42652afea99a2ec6c595a", "0x12f4175c4ab45afc196e41859b35ef88812c3286ee7000675a0563b9b8e9f1d5", "0x3a509e155cb7ebfd8f8fdcf800a9ac697e23e1aabe96cfab0e74d4d369118b79"], ["0x10f2a685df4a27c81a89920e2504c3b3984bc8f2e4c1b69e98712c65678cfd30", "0x9e5f49790c8a0e21d8d93d54ab91a0e54573c9333c56321e8a16728cc9d4918", "0x352d69bed80ee3e52bf35705d9f84a3442d17ed6ee0fab7e609a740347cf5fea"], ["0x58ee73ba9f3f293491562faf2b190d3c634debd281b76a63a758af6fa84e0e8", "0x232f99cc911eddd9cd0f1fc55b1a3250092cb92119bc76be621a132510a43904", "0x201beed7b8f3ab8186c22c6c5d4869f0f9efd52ca6bc2961c3b97c1e301bc213"], ["0x1376dce6580030c6a1c9291d58602f5129388842744a1210bf6b3431ba94e9bc", "0x1793199e6fd6ba342b3356c38238f761072ba8b02d92e7226454843c5486d7b3", "0x22de7a7488dcc7359fee9c20c87a67df3c66160dc62aacac06a3f1d3b433311b"], ["0x3514d5e9066bb160df8ff37fe2d8edf8dbe0b77fae77e1d030d6e3fd516b47a8", "0x30cd3006931ad636f919a00dabbf5fa5ff453d6f900f144a19377427137a81c7", "0x253d1a5c5293412741f81a5cf613c8df8f9e4b2cae2ebb515b6a74220692b506"], ["0x35b461c02d79d19a35e9613e7f5fe92851b3a59c990fafc73f666cb86a48e8e", "0x23a9928079d175bd5bc00eedd56b93e092b1283c2d5fccde7cfbf86a3aa04780", "0x13a7785ae134ea92f1594a0763c611abb5e2ea3436eef957f1e4ccd73fa00a82"], ["0x39fce308b7d43c574962ae3c0da17e313889c57863446d88bbf04f5252de4279", "0x1aae18833f8e1d3ac0fdf01662f60d22bef00a08c6ed38d23b57e34489b53fad", "0x1a761ce82400af018b2e80c064fd83ed27c1b3fd8f85d8a855513e033398513f"], ["0x275a03e45adda7c316dd1a87ca22e1ccdcf6af2830a502875244ca749b73e481", "0x2e5a10f08b5ab8bbeb08e47e5feabcf807e561453fc5648b58a253cfb6a95786", "0x1459cb8587208473b84e9c333b2932f1c141a5b6d594bec4e033d82cefe78ce3"], ["0x193ae5921d78b5de7b92ce810e14a40052f9332fbffcfbbd5cec7e7b338fbe1b", "0x3097898a5d0011a489111fb2c4660281374384f4a072820560224be67248e82c", "0x378d97bf8c864ae7571782fd96ce54b41979b2d1c465b4d9549980de862930f5"], ["0x2eb04ea7c01d97ec88136287ce376b08dbc7f5cb4609342137ea32a971d17884", "0x36425347ea03f6412302a1c22e49baec861cbda476804e6cead3726f1af2e7b0", "0x26b72df47408ad42cc996cd85c98a1d83f5b5ca5a19a9701ecd627e59590d09e"], ["0x130180e44e2924db1f05636c610b89aade01212ee4588f8959bece31f0a31e95", "0x219e97737d3979ba73275acaed5f579cdf7793cc89e5b52f9ea8e7bc79263550", "0x3cdb93598a5ca5283461363f81c489a23b0672dd7d42cbb49c12635df251d153"], ["0xe59e6f332d7ed3720724b927a0ca81c4ad0447045a7c5aa2861ce16f219d5a9", "0x1b064342d51a42753d7369467222697a172cc07b9d33fbf943b0a3fcff2036bd", "0x30b82a998cbd8e8a2f363c55b2882e0b78fa9fb9171221b73eb310228a0e5f6c"], ["0x23e4ab37183acba463df7a76e858a4aa8ad71ea715be0573e46f6d4298740107", "0x2795d5c5fa4280225d33094e0beda75bacfe14640de044f2fca995e2b59914a1", "0x3001ca401e89601cd765f26dd03f4c45a6687c3df16c8fe4c26d909dee8b53c0"], ["0x72e45cc676b08ef7bf86e89280827fe84b5bebae4e501de7fea6bdf3471380", "0x13de705484874bb5e2abe4c518ce599eb64829e2d40e41bdd0c54ddeb26b86c0", "0x408a9fcf9d61abf315950f1211defe882bb18e5af1b05bb38915b432a9959a5"], ["0x2780b9e75b55676ebb4e4a1400ccd2c4ae4d23b0b41be9a834070cbee26886a0", "0x3a570d4d7c4e7ac3f80333ec85634ac9dc4d8fbefe24405a9405592098b4056f", "0xc13cca7cb1f9d2cf347c247fcf09294e2cc1507bebdcc6278d2b247899520b4"], ["0x14f59baa03cd0ca4d2614a197c6b794b0b50bb2eb82df74d2e8c88f7707470e0", "0x307defee925dfb436f546e1704c39c60a51d54ede66167f5be52476e0a16f3be", "0x1960cd511a91e0607a07e7674b5a2621661106836adfe5e7380b67d80473dce3"], ["0x2301ef9c63ea84c5ca2ad0fb56672500b8ee335d88284cbe15aaf1f7712589dd", "0x29a5a47da79a488d10f4cd52be97f6bc86182d1b4246b585e68478c4d6027a9", "0x32d7b16a7f11cc962360d17d890e55cbf97fe46b6a9254282cc4f962eaae2260"], ["0x26703e48c03b81ca18e857a98d498cf7a5f2404cd7b35eb0c0cab915d5363d9f", "0x48682a35b3265bc88ac8d25a24603f1f44388bd6b89221ef691123ae112b928", "0x6b1390441fa7030d72cddc6cf06b50791d6e1715164775e3ab7defcb8d803e2"], ["0x31aa0eeb868c626d1689426dce05fcd843b360f6386a86d7bcd795414a6e2e86", "0x239464f75bf7b6af057abad3764c104b90efd8f41b2078b2ed77f5d576b99cc3", "0xa64d4c04fd426bda45e19ed813a54aba5cc47c59654b2a7b2cb487307c1cecf"], ["0x21fbbdbb73670734576a4ad259860fb1777c7a921a062e9d1f7315322f658735", "0x31b86f3cf01705d4d9371ca2eb95acf35b86d29463d31564674324003fc52146", "0x2bfde53354377c9105ef1736d09056f613541d65157ee1ce7045f48aa4eb4f6f"], ["0x1233ca936ec24671d558f36e65f8eca7f4d5239c11d0eafa5a13a58d20011e2f", "0x27d452a43ac7dea2c437846d8e0b2b30878058d0234a576f6e70af0a7a924b3a", "0x2699dba82184e413e816ea8da493e0fa6a30641a1c3d87b2a02576b94392f980"], ["0x36c722f0efcc8803c3988baee42e4b10f18584664f8cab49608c6f7a61b56e55", "0x2b3ff48861e339b08b0f2ec89ccaa3785c38899a7b5a8336e49ac170dbb7fcd", "0xb70d061d58d8a7f60162f4427bc657b6fc3ff4c49eb59ada8c5ae03ad98e405"], ["0x3fc2a13f127f96a4f8753adeb9d7cee2ad3de8be46ed96932e06cc4af33b0a06", "0xc41a6e48dd23a511bd63434ac8c419f00cb3d621e171d80c12080ac117ee15f", "0x2de8072a6bd86884ed4476537169084e72aaad7e4e75339d9685213e9692f5e1"], ["0x3557a8f7b38a17f9d3496a3d9fe05ecb81cf735cc9c39c00ad01184567b027c", "0xb5f59552f498735ee976d34282f1a37060f43363d818e5445bcb5ac00826abc", "0xe2923a5fee7b878fedbb18570dc7300f5d646e57507e5482f2909e17e22b0df"], ["0x1d785005a7a00592c787be97020a7fddcf1cb37c3b032af6f71eed73f15b3326", "0x1ad772c273d9c6df0ba5fedcb8f25bd2a590b88a3b0602940acfbfb223f8f00d", "0x27bd64785fcbd2aa78f3275c278234b810510eb61f0672dc1ce13d60f2f5031"], ["0x20800f441b4a0526ce6f8ffea1031b6de224313469457b8e8337f5e07923a853", "0x3d5ad61d7b65f9386eea2cd49f4312b436cdc8eed662ad37a33d7bed89a4408a", "0x13338bc351fc46dd02c5f91be4dd8e3d1df96cc03ea4b26d3bbbae94cc195284"], ["0x25e52be507c92760b87db1e2af3ea923646c49f9b46cbf19c5271c297852819e", "0x1c492d64c157aaa471096d8b1b983c98a34c83a3485c6b2d5c380ab701b52ea9", "0xc5b801579992718f4e6c5e7a573f592d43487bc288df682a20c0b3da0da4ca3"], ["0x1090b1b4d2bebe7a68695c0cd7cbf43d584e9e62a7f9554e7ea33c93e40833cf", "0x33e38018a801387a68f5ce5cbed19cad1b218e35ecf2328ee383e1ec3baa8d69", "0x1654af18772b2da5eef8d83d0e876bac5f4a02d28729e3aeb76b0b3d787ee953"], ["0x1678be3cc9c6799344742de88c5ab0d5bb0893870367ec6cef7ce6a013265477", "0x3780bd1e01f34c227ff9c6be546e928adaf1818355b13b4faf5d47893348f766", "0x1e83d6315c9f125b0786018e7cb772675d11e69aa6c0b98ca12380320d7cc1de"], ["0x354afd0a2f9d0b26160b41552f2931c8c486894d76e0c33b1799603e855ce731", "0xcd6d29f166eadc2d8affa62905c5a560b00dbe1faced078b997ee06be1bff3", "0x1d6219352768e3aedbe0e3d7cdbc66efc60d01973f18305708d0641917082f2c"], ["0x146336e25db5181de48d2370d7d1a142afe3ca1db8d4f529fa08dd9806387577", "0x5d8e085fd72ee997a21163e2e43df022e54b49c13d907a901d3ce84de0ad4", "0x364e97c7a38932270dd5e61c8a4e86426f8ebc1d2296021a1c36f31341964484"], ["0x1189910671bc16b561c6fff15346878fa97ec80ad307a52d7a00c03d2e0baaa", "0x162a7c80f4d2d12e5229dfaa01231a454c0f7e001df490aa63fd8ac57a95ca8c", "0x2a0d6c09576666bb2604e4afb09f8603caff31b4fda3212432e69efb22f40b96"], ["0x978e5c51e1e5649e16a4d603d5a808ef444d10d63a74e2cc0a0180f8cbfc0d2", "0x1bdcee3aaca9cd25ebe19bbdce25101105087d903bdacfd103f4460ebc351b6e", "0x1862cccb70b5b885e49479140b1944fd0c947321e0075e3ff61964bf3ade7670"], ["0x1f3e91d863c16922bc26cc883a1987e139ee99c1cc6e5ddac3267da6e94adc50", "0x1af47a48a6016a49ef5c08f8478f663afa661465c656ad990f85b4ac2c367406", "0x3c8ee901956e3d3f009d57338c6935051c3698b0a2e3da100eabcd87e7d01b15"], ["0x1660a8cde7fec55368d0b024f591b520e10ce2b7069f4dbd8b94772189673476", "0xf6d991929d5e4e71303936334dd11323963c2c1f5586e2f9d8d0f67fdaa79d5", "0x2b9cea1921cd9f6cc625eaaab52b4dc4e7fda770712f3437a433091e1ce2d3a"], ["0x14a323b99b900331214f7c6784acb565d8caf468976f04723797b2d8376043b3", "0x190476b580cb9277ec01ea79642d5760718b7fbc7788af78347fef2c00f0953a", "0x90a3a9d869d2eefa42463d30b442b6f9660902b60087651ff4e7e6fb268dfd7"], ["0x3877a955863675670dbe8fd2270a6795e365001304f9a11ef983387ea0456203", "0x2d894691240fe9535df39a2cc63ddc0a60118c53a218135239c0af0fe01f4a06", "0x21b9c18292bdbc597ef71780201661895914e855eeb44aa11aca9eaf9bba9850"], ["0x2fe76be7cff723e2505a05f2a6ae834c272e1cc6c36a296833f509a74ad9d39b", "0x187aa448f391e3ca929981d7cfce253bd15bff840ddae8a50df9fa97277fa8b4", "0xb7083ad751707bf007ab3aa3617f422663ccf7b2ffe4b5ef0c66af5ffc73736"], ["0x30ddbb470493f163bc4ca9902c52acb1975b962f6cb8e0b2f9b20f1fbd49791", "0x3130fbaffb5aa82a950b0ab18d3546df8fb8ab9d60ea17b23a1c62ca8fbf2525", "0x337f544707c430f04f74d74bac2ee45715ce2ead2fcd051e43a876180dc382e0"], ["0x349979919015394fac9d91b0930dac757d8e471a9fb95fef26de98a8736d1d11", "0x27cc4efe3fb35dd2305cd7a921ec5f13bf93da6fff31d95ccfcb61831d5c775", "0x37f9f2365954c5b61b71a3698682ad267f1c6b7314764afc3fa2629635d27de"], ["0x1f697cac4d07feb710f1cc6df8b4bcd760414abe362d01c977c5b024848371ae", "0x267a750fe5d7cfbc26e6c851fbd572a63145c478063109d6786add244aa0ef29", "0xc91feab4a43193a678c9996d9a472c8af285fa82ce4fae5180e2b4d3e756f65"], ["0x1745569a0a3e30142186c3038ea05e697e3b83af4a4ba3ba79c47c573ac410f7", "0x29863d546e7e7c0deca5120778a56711fdff66c6f3b5ffe11e0388522696191f", "0x1148d6ab2bd00192bf06bae49ef853f6a79a03df833994c62f225e6366bfe390"], ["0x2e0e121b0f3dfefe18b1499060da366f745f45d350d41d4f4f6331a8b265d15", "0xd0aa46e76a6a278b89ef73a40a2b274690401736d44a653078ae6aa151054b7", "0x13943675b04aa986eee545f3fa6d3d08392dde710f1f06db9a4d532c7b6e0958"], ["0x2901ec61942d34aad97a11d63088f5d9c9f2b3257530dafe961fc818dcbb66b5", "0x20204a2105d22e7ef431d54434a3e0cf22ffa2a2af9fa3e3fdf544b963d1fdc7", "0x3a8a628295121d5c5c1e3e9e27a571c3a004abe8e01528c41211b9e2190d6852"]], "mds": [["0xab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63", "0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e", "0x7c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d"], ["0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c", "0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e", "0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a"], ["0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4", "0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664", "0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1"]]}
"""step.py - the equivalent straight-line step program for the r-partial-round Orchard hash on the two-round line.

Walk map: F(x) = digest(message(x + rho0)) / OUTSCALE. On the line (round-0 S-box outputs (A, B) = (T + A0, mu5 T + B0),
k = 2 the constant lane of the round-1 S-box input), with W = T^5 the state after round 1 is A1 + W B1. The program
computes F(x) from x with lanes held divided by known scales:

  enter        t_i = x + K_i                                   (3 additions; K_i = rho0 + (A1_i + c2_i)/B1_i per attempt)
  full round   y_i = t_i^5 (9 mul); t'_i = y_{j_i} + k_i1 y_. + k_i2 y_. + kappa_i   (per lane 2 mul + 3 add) = 24
  last full    only lane 0: y0..y2 (9 mul), out = y0 + k1 y1 + k2 y2 (2 mul + 2 add) = 13
  into partial (after the last full round before the partial rounds): lane 0 as a full-round lane (5), the passive
               lanes in the basis zeta = Q y + q (2 rows, one coefficient 1 each: 2 x 5)
  partial      y = t0^5 (3 mul); t0' = y + l1 z1 + l2 z2 + kappa (2 mul + 3 add); z_i += g_i y (2 mul + 2 add) = 12
  out of partial: with the passive basis P_60 diagonal and the offset absorbed, t1 = z1, t2 = z2 (0 operations)
Total for r partial rounds: 3 + 24 (round 2) + 24 (round 3, into partial form) + 12 r + 0 + 3 * 24 (rounds 60-62)
+ 13 (round 63) = 136 + 12 r; r = 30: 496 field operations.

Program format: list of (op, dst, a, b) with op in {'add', 'mul'}; operands are register names; constants live in
registers 'k<i>' (loaded once per attempt). build(r, consts, rho0) returns (program, constant table, OUTSCALE) and
verify() checks F(x) * OUTSCALE == digest(message(x + rho0)) against the reference permutation.
"""
import json, os, sys
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
inv = lambda x: pow(x % P, P - 2, P)
E5 = pow(5, -1, P - 1)
HERE = os.path.dirname(os.path.abspath(__file__))
CPATH = os.path.join(HERE, '..', '..', 'pareto', 'orchard-pallas-constants.json')


def load():
    C = EMBEDDED
    RC = [[int(x, 16) for x in row] for row in C['round_constants']]
    M = [[int(x, 16) for x in row] for row in C['mds']]
    return RC, M


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) % P for j in range(len(B[0]))] for i in range(len(A))]


def matinv2(A):
    d = (A[0][0] * A[1][1] - A[0][1] * A[1][0]) % P
    di = inv(d)
    return [[A[1][1] * di % P, -A[0][1] * di % P], [-A[1][0] * di % P, A[0][0] * di % P]]


class Line:
    """the two-round line (lane k = 2 constant at the round-1 S-box input)."""
    def __init__(self, RC, M, r):
        self.RC, self.M, self.r = RC, M, r
        CAP = 1 << 65; self.CAP = CAP
        k = 2
        K5 = pow((CAP + RC[0][2]) % P, 5, P)
        i, j = 0, 1
        mu5 = (-M[k][0] * inv(M[k][1])) % P
        a, b, e = M[i][0], M[i][1], (-(M[i][2] * K5 + RC[1][i])) % P
        c, d, f = M[j][0], M[j][1], (-(M[j][2] * K5 + RC[1][j])) % P
        det = (a * d - b * c) % P; di = inv(det)
        A0 = ((e * d - b * f) * di) % P; B0 = ((a * f - e * c) * di) % P
        self.mu5, self.A0, self.B0 = mu5, A0, B0
        slope = [(M[t][0] + M[t][1] * mu5) % P for t in range(3)]
        constk = (M[k][0] * A0 + M[k][1] * B0 + M[k][2] * K5 + RC[1][k]) % P
        assert slope[k] == 0 and slope[0] and slope[1]
        sb_lin = [pow(slope[t], 5, P) if t != k else 0 for t in range(3)]
        sb_const = [pow(constk, 5, P) if t == k else 0 for t in range(3)]
        self.A1 = [sum(M[row][col] * sb_const[col] for col in range(3)) % P for row in range(3)]
        self.B1 = [sum(M[row][col] * sb_lin[col] for col in range(3)) % P for row in range(3)]
        assert all(self.B1)

    def message(self, W):
        T = pow(W, E5, P)
        A = (T + self.A0) % P; B = (self.mu5 * T + self.B0) % P
        return (pow(A, E5, P) - self.RC[0][0]) % P, (pow(B, E5, P) - self.RC[0][1]) % P

    def digest(self, m0, m1):
        s = [m0, m1, self.CAP]
        for idx in (*range(4), *range(4, 4 + self.r), *range(60, 64)):
            s = [(x + c) % P for x, c in zip(s, self.RC[idx])]
            for col in (range(3) if idx < 4 or idx >= 60 else range(1)):
                s[col] = pow(s[col], 5, P)
            s = [sum(c * x for c, x in zip(row, s)) % P for row in self.M]
        return s[0]


def build(r, rho0=None):
    RC, M = load()
    L = Line(RC, M, r)
    prog = []          # (op, dst, a, b)
    consts = {}        # name -> value (loaded once per attempt)
    cnt = [0]

    def K(v):
        name = 'k%d' % len(consts)
        consts[name] = v % P
        return name

    def op(o, d, a, b):
        prog.append((o, d, a, b))

    def pow5(src, dst):
        op('mul', dst + 's', src, src); op('mul', dst + 'q', dst + 's', dst + 's'); op('mul', dst, dst + 'q', src)

    # enter: actual round-2 S-box input u_i = A1_i + c2_i + W B1_i = B1_i (W + K_i), W = x + rho0
    beta = list(L.B1)
    kin = [(L.A1[i] + RC[2][i]) * inv(L.B1[i]) % P for i in range(3)]
    rho0 = rho0 or 0
    for i in range(3):
        op('add', 't%d' % i, 'x', K(kin[i] + rho0))
    # helper: one full round from stored t (actual = beta * t) to next S-box inputs (with constants of round nxt)
    def full_round(beta, nxt_const):
        for i in range(3):
            pow5('t%d' % i, 'y%d' % i)
        sc = [pow(b, 5, P) for b in beta]                       # actual y_i = sc_i * y_i
        coef = [[M[i][j] * sc[j] % P for j in range(3)] for i in range(3)]
        newbeta = []
        for i in range(3):
            j0 = 0
            nb = coef[i][j0]; newbeta.append(nb); ni = inv(nb)
            ks = [coef[i][j] * ni % P for j in range(3)]
            kap = nxt_const[i] * ni % P
            op('mul', 'm%da' % i, 'y1', K(ks[1])); op('mul', 'm%db' % i, 'y2', K(ks[2]))
            op('add', 'm%dc' % i, 'y0', 'm%da' % i); op('add', 'm%dd' % i, 'm%dc' % i, 'm%db' % i)
            op('add', 'n%d' % i, 'm%dd' % i, K(kap))
        for i in range(3):
            op('add', 't%d' % i, 'n%d' % i, 'ZERO') if False else None
        # rename n_i -> t_i (register renaming is free: emit as aliases)
        prog.append(('alias', None, None, None))
        return newbeta, coef
    # round 2 (full) -> constants of round 3
    beta, _ = full_round(beta, RC[3])
    # round 3 (full) into partial form (round 4 constants) -- or, if r == 0, into round 60
    if r == 0:
        beta, _ = full_round(beta, RC[60])
        rounds_tail = [60, 61, 62]
    else:
        # round 3: S-box, then MDS; lane 0 -> t0 scaled with constant c4_0; passive lanes -> zeta basis
        for i in range(3):
            pow5('t%d' % i, 'y%d' % i)
        sc = [pow(b, 5, P) for b in beta]
        coef = [[M[i][j] * sc[j] % P for j in range(3)] for i in range(3)]   # out = coef * y
        # partial-round sparse form: M = [[a, b^T],[e, D]]
        a_ = M[0][0]; bvec = [M[0][1], M[0][2]]; evec = [M[1][0], M[2][0]]; Dm = [[M[1][1], M[1][2]], [M[2][1], M[2][2]]]
        # passive basis: z_r = P_r zeta + o_r, P_{r+1} = D P_r; P_60 diagonal => P_4 = D^-(r) diag(s)
        Dinv = matinv2(Dm)
        Dn = [[1, 0], [0, 1]]
        for _ in range(r):
            Dn = matmul(Dn, Dinv)                               # D^-r
        # zeta at round 4: zeta = P_4^-1 (z_4 - o_4), z_4 = coef[1:3] y + c4[1:3]; P_4 = D^-r S, S = diag(s1, s2)
        # => zeta = S^-1 D^r (coef[1:3] y + c4[1:3] - o_4); choose s_i to normalise the first coefficient of row i
        Dr = [[1, 0], [0, 1]]
        for _ in range(r):
            Dr = matmul(Dr, Dm)
        rows = matmul(Dr, [coef[1], coef[2]])                   # 2 x 3
        s = [rows[0][0], rows[1][0]]
        P4 = matmul(Dn, [[s[0], 0], [0, s[1]]])
        # offsets: choose o_4 so that o_60 (the offset at the exit) is zero: o_{r+1} = D o_r + c_{r+1}[1:3]
        # o_60 = D^r o_4 + sum_{j} D^(r-1-j) c_{5+j}[1:3]  (constants of rounds 5..59 and 60) = 0
        acc = [0, 0]
        for rr in range(5, 4 + r):                              # constants added at rounds 5..3+r (passive lanes)
            acc = [(Dm[0][0] * acc[0] + Dm[0][1] * acc[1] + RC[rr][1]) % P, (Dm[1][0] * acc[0] + Dm[1][1] * acc[1] + RC[rr][2]) % P]
        acc = [(Dm[0][0] * acc[0] + Dm[0][1] * acc[1] + RC[60][1]) % P, (Dm[1][0] * acc[0] + Dm[1][1] * acc[1] + RC[60][2]) % P]
        # D^r o_4 + acc = 0 => o_4 = -D^-r acc
        o4 = [(-(Dn[0][0] * acc[0] + Dn[0][1] * acc[1])) % P, (-(Dn[1][0] * acc[0] + Dn[1][1] * acc[1])) % P]
        P4inv = matinv2(P4)
        # zeta = P4inv (coef[1:3] y + c4[1:3] - o4)
        zrow = matmul(P4inv, [coef[1], coef[2]])
        zc = [(P4inv[i][0] * (RC[4][1] - o4[0]) + P4inv[i][1] * (RC[4][2] - o4[1])) % P for i in range(2)]
        for i in range(2):
            assert zrow[i][0] == 1
            op('mul', 'z%da' % i, 'y1', K(zrow[i][1])); op('mul', 'z%db' % i, 'y2', K(zrow[i][2]))
            op('add', 'z%dc' % i, 'y0', 'z%da' % i); op('add', 'z%dd' % i, 'z%dc' % i, 'z%db' % i)
            op('add', 'z%d' % (i + 1), 'z%dd' % i, K(zc[i]))
        # lane 0 for round 4: actual S-box input = coef[0] y + c4_0 = b0 * t0, b0 = coef[0][0]
        b0 = coef[0][0]; ni = inv(b0)
        op('mul', 'm0a', 'y1', K(coef[0][1] * ni)); op('mul', 'm0b', 'y2', K(coef[0][2] * ni))
        op('add', 'm0c', 'y0', 'm0a'); op('add', 'm0d', 'm0c', 'm0b'); op('add', 't0', 'm0d', K(RC[4][0] * ni))
        Pr = P4; o = o4; bcur = b0
        for rr in range(4, 4 + r):
            # actual lane0 S-box input = bcur * t0; y = t0^5 (actual sc * y)
            pow5('t0', 'y')
            scv = pow(bcur, 5, P)
            # next lane 0: a sc y + b^T (Pr zeta + o) + c_{next,0}
            nxt = RC[rr + 1] if rr + 1 < 4 + r else RC[60]
            ell = [(bvec[0] * Pr[0][j] + bvec[1] * Pr[1][j]) % P for j in range(2)]
            const0 = (bvec[0] * o[0] + bvec[1] * o[1] + nxt[0]) % P
            nb = a_ * scv % P; ni = inv(nb)
            op('mul', 'pa', 'z1', K(ell[0] * ni)); op('mul', 'pb', 'z2', K(ell[1] * ni))
            op('add', 'pc', 'y', 'pa'); op('add', 'pd', 'pc', 'pb'); op('add', 't0', 'pd', K(const0 * ni))
            # passive update: zeta += P_{r+1}^-1 e sc y
            Pn = matmul(Dm, Pr)
            g = matmul(matinv2(Pn), [[evec[0] * scv % P], [evec[1] * scv % P]])
            op('mul', 'qa', 'y', K(g[0][0])); op('mul', 'qb', 'y', K(g[1][0]))
            op('add', 'z1', 'z1', 'qa'); op('add', 'z2', 'z2', 'qb')
            o = [(Dm[0][0] * o[0] + Dm[0][1] * o[1] + nxt[1]) % P, (Dm[1][0] * o[0] + Dm[1][1] * o[1] + nxt[2]) % P]
            Pr = Pn; bcur = nb
        # exit: z_60 = Pr zeta + o with Pr = diag(s), o = 0 => actual round-60 S-box inputs lanes 1,2 = s_i zeta_i
        assert Pr[0][1] == 0 and Pr[1][0] == 0 and o == [0, 0], (Pr, o)
        prog.append(('rename', 't1', 'z1', None)); prog.append(('rename', 't2', 'z2', None))
        beta = [bcur, Pr[0][0], Pr[1][1]]
        rounds_tail = [60, 61, 62]
    for rr in rounds_tail:
        beta, _ = full_round(beta, RC[rr + 1])
    # round 63: only lane 0
    for i in range(3):
        pow5('t%d' % i, 'y%d' % i)
    sc = [pow(b, 5, P) for b in beta]
    coef0 = [M[0][j] * sc[j] % P for j in range(3)]
    outscale = coef0[0]; ni = inv(outscale)
    op('mul', 'oa', 'y1', K(coef0[1] * ni)); op('mul', 'ob', 'y2', K(coef0[2] * ni))
    op('add', 'oc', 'y0', 'oa'); op('add', 'out', 'oc', 'ob')
    return L, prog, consts, outscale


def run(prog, consts, x):
    """execute the program; aliases: full_round writes n_i which become t_i at the 'alias' marker."""
    reg = dict(consts); reg['x'] = x
    for o, d, a, b in prog:
        if o == 'mul':
            reg[d] = reg[a] * reg[b] % P
        elif o == 'add':
            reg[d] = (reg[a] + reg[b]) % P
        elif o == 'alias':
            for i in range(3):
                reg['t%d' % i] = reg['n%d' % i]
        elif o == 'rename':
            reg[d] = reg[a]
    return reg['out']


def count(prog):
    n_add = sum(1 for p in prog if p[0] == 'add'); n_mul = sum(1 for p in prog if p[0] == 'mul')
    return n_add, n_mul


ODIGEST = None
checked = [0]


def verify(r, trials=8, rho0=12345):
    import random
    L, prog, consts, outscale = build(r, rho0)
    rnd = random.Random(r)
    for _ in range(trials):
        x = rnd.randrange(P)
        W = (x + rho0) % P
        m = L.message(W)
        ref = L.digest(*m)
        got = run(prog, consts, x)
        assert got * outscale % P == ref, (r, x)
        if ODIGEST is not None:                       # the organizer's verifier, when run inside the repository
            msg = m[0].to_bytes(32, 'little') + m[1].to_bytes(32, 'little')
            assert ODIGEST(msg, r) == (got * outscale % P).to_bytes(32, 'little')
            checked[0] += 1
    a, mm = count(prog)
    return a, mm, len(consts)



"""machine.py - the r = 30 search as an instruction listing for a declared register machine, with a counting interpreter.

Machine (proof Section 7, H2): registers R[0..511] of 256 bits, word memory MEM, 32-bit instructions
(5-bit opcode, three 9-bit fields). Costs per executed instruction:
  ADD SUB MUL (field, canonical result)            1      IADD ISUB (integer, mod 2^256)      1
  IADDI d,a,imm9                                   1      MOV d,a                             1
  AND OR d,a,b                                     1      SHRV SHLV d,a,b (shift by R[b])     1
  LD d,a  (d = MEM[R[a]])                          2      ST a,b  (MEM[R[a]] = R[b])          2
  BLT BEQ BNE a,b,t (compare, branch to R[t])      2      JMP t (to R[t])                     1
  RAND d (one random 256-bit word)                 1      HALT code                           1
Jump targets are held in registers (loaded at setup from constant memory). build_program() emits the listing for the
search of proof Section 3 with the real step program (step.py); run() executes it and counts every instruction.
For reduced-width tests (trunc=w), one AND X, X, MASKW follows every step-program instance (test builds only).
"""
import math
build_step = build

OPS = {'ADD': 1, 'SUB': 1, 'MUL': 1, 'IADD': 1, 'ISUB': 1, 'IADDI': 1, 'MOV': 1, 'AND': 1, 'OR': 1, 'SHRV': 1, 'SHLV': 1,
       'LD': 2, 'ST': 2, 'BLT': 2, 'BEQ': 2, 'BNE': 2, 'JMP': 1, 'RAND': 1, 'HALT': 1}
M256 = (1 << 256) - 1
E5 = pow(5, -1, P - 1)


class Gen:
    def __init__(self):
        self.code = []          # (op, a, b, c)
        self.labels = {}
        self.regs = {}
        self.consts = []        # (register, value or ('label', name))

    def reg(self, name):
        if name not in self.regs:
            self.regs[name] = len(self.regs)
            assert len(self.regs) <= 512, 'register file exhausted'
        return self.regs[name]

    def emit(self, op, a=0, b=0, c=0):
        self.code.append([op, a, b, c])

    def label(self, name):
        self.labels[name] = len(self.code)

    def target(self, name):
        """register holding the address of label name (loaded at setup)."""
        r = self.reg('T:' + name)
        if ('label', name) not in [v for _, v in self.consts if isinstance(v, tuple)]:
            self.consts.append((r, ('label', name)))
        return r

    def const(self, name, value):
        r = self.reg(name)
        self.consts.append((r, value))
        return r


def build_program(Delta, S, MCAP, G, GPOS, VB, WG, K=15, trunc=None, r=30, rho_bits=254, digest_trunc=False):
    """two passes: the first collects every jump target, the second registers them before the constant-loading code."""
    first = _build(Delta, S, MCAP, G, GPOS, VB, WG, K, trunc, r, rho_bits, [], digest_trunc)
    targets = [nm for nm in first['target_names']]
    return _build(Delta, S, MCAP, G, GPOS, VB, WG, K, trunc, r, rho_bits, targets, digest_trunc)


def _build(Delta, S, MCAP, G, GPOS, VB, WG, K, trunc, r, rho_bits, pre_targets, digest_trunc=False):
    g = Gen()
    L, prog, consts, outscale = build_step(r, 0)
    # step-program registers: constants k<i> first (registers 0..329), then the step's own names
    for i in range(len(consts)):
        g.const('k%d' % i, consts['k%d' % i])
    X = g.reg('X')
    # register allocation of the step program: SSA values, freed at their last use, physical scratch registers reused
    env = {'x': ('in',)}
    seq = []
    vid = 0
    for o, d, a, b in prog:
        if o in ('add', 'mul'):
            sa = env[a] if not (a.startswith('k') and a[1:].isdigit()) else ('k', a)
            sb = env[b] if not (b.startswith('k') and b[1:].isdigit()) else ('k', b)
            vid += 1; v = ('v', vid)
            seq.append(('ADD' if o == 'add' else 'MUL', v, sa, sb)); env[d] = v
        elif o == 'alias':
            for i in range(3):
                env['t%d' % i] = env['n%d' % i]
        elif o == 'rename':
            env[d] = env[a]
    outv = env['out']
    last = {}
    for i, (_, v, sa, sb) in enumerate(seq):
        last[sa] = i; last[sb] = i
    free, phys, maxlive = [], {}, [0]
    pool = []
    def preg(v):
        if v == ('in',):
            return X
        if v[0] == 'k':
            return g.regs[v[1]]
        return phys[v]
    alloc = []
    for i, (op, v, sa, sb) in enumerate(seq):
        ra, rb = preg(sa), preg(sb)
        for s_ in ({sa, sb}):
            if s_[0] == 'v' and last.get(s_) == i and s_ in phys and phys[s_] != X:
                free.append(phys[s_])
        if v == outv:
            rd = X
        else:
            if not free:
                pool.append(g.reg('s%d' % len(pool))); free.append(pool[-1])
            rd = free.pop()
        phys[v] = rd
        alloc.append((op, rd, ra, rb))
    STEP_SCRATCH = len(pool)

    def emit_step():
        for op, rd, ra, rb in alloc:
            g.emit(op, rd, ra, rb)
        if trunc is not None:
            if digest_trunc:
                g.emit('MUL', X, X, g.regs['OUTS'])        # test builds only: walk on the low bits of the digest itself
            g.emit('AND', X, X, g.regs['MASKW'])

    # constants and parameters
    ZERO = g.const('ZERO', 0); ONE = g.const('ONE', 1)
    C256 = g.const('C256', 256); C255 = g.const('C255', 255); C8 = g.const('C8', 8)
    DELTA = g.const('DELTA', Delta); SCAPR = g.const('SCAP', S); MCAPR = g.const('MCAP', MCAP)
    GR = g.const('G', G); GPOSR = g.const('GPOS', GPOS); LIMWG = g.const('LIMWG', 1 << WG)
    VBR = g.const('VB', VB); WGR = g.const('WG', WG)
    MV = g.const('MASKV', (1 << VB) - 1); MG = g.const('MASKG', (1 << WG) - 1)
    MR = g.const('MASKRHO', (1 << rho_bits) - 1)
    GB = g.const('GAPBASEBIT', 0)                    # set below (bit offset of the gap array)
    E5R = g.const('E5', E5); TOPBIT = g.const('TOPBIT', 1 << (E5.bit_length() - 1))
    A0R = g.const('A0', L.A0); B0R = g.const('B0', L.B0); MU5 = g.const('MU5', L.mu5)
    C00 = g.const('C00', (P - L.RC[0][0]) % P); C01 = g.const('C01', (P - L.RC[0][1]) % P)
    if trunc is not None:
        g.const('MASKW', (1 << trunc) - 1)
        if digest_trunc:
            g.const('OUTS', outscale)
    for nm in ('BASE', 'POS', 'I', 'CNT', 'LAST', 'RET', 'RET2', 'RHO', 'X0', 'BPV', 'BPG', 'IDX', 'PIDX', 'PVAL', 'E', 'V', 'GV',
               'W0', 'W1', 'WI', 'OFF', 'T1', 'T2', 'GAP', 'I1', 'LAM', 'TB', 'BIDX', 'BVAL', 'DIST', 'CC', 'A', 'B', 'FA',
               'ADDR', 'RR', 'WW', 'BM', 'TT', 'XA', 'XB', 'M0', 'M1', 'OUTA'):
        g.reg(nm)
    R = g.regs
    words_v = -(-(MCAP * VB) // 256); words_g = -(-(MCAP * WG) // 256)
    TABLE_WORDS = words_v + words_g + 1
    gap_base_word = words_v
    X0ADDR = TABLE_WORDS                              # start word
    CBASE = X0ADDR + 1                                # constant memory
    ADDRX0 = g.const('ADDRX0', X0ADDR)
    TW = g.const('TABLEWORDS', TABLE_WORDS)
    # ---------------- setup: load constants (straight line), zero the table, coins
    g.label('start')
    for nm in pre_targets:
        g.target(nm)
    # constant loading: ADDR <- CBASE is itself loaded by IADDI chains? use a dedicated literal at register 'ADDR' = CBASE:
    # the machine starts with R all zero and PC 0; ADDR = CBASE is formed by IADDI steps of 511 (charged).
    rem = CBASE
    while rem > 0:
        st = min(rem, 511)
        g.emit('IADDI', R['ADDR'], R['ADDR'], st); rem -= st
    nconst_slot = []
    for reg_, val in g.consts:
        nconst_slot.append((reg_, val))
        g.emit('LD', reg_, R['ADDR'])
        g.emit('IADDI', R['ADDR'], R['ADDR'], 1)
    # zero the table (memory may hold data; every table word is written)
    g.emit('MOV', R['ADDR'], ZERO)
    g.label('zl')
    g.emit('ST', R['ADDR'], ZERO); g.emit('IADDI', R['ADDR'], R['ADDR'], 1)
    g.emit('BNE', R['ADDR'], TW, g.target('zl'))
    g.label('zl_end')
    # coins
    g.emit('RAND', R['RHO']); g.emit('AND', R['RHO'], R['RHO'], MR)
    g.emit('RAND', R['X0']); g.emit('AND', R['X0'], R['X0'], MR)
    if trunc is not None:
        g.emit('AND', R['X0'], R['X0'], R['MASKW'])
    g.emit('ST', ADDRX0, R['X0'])
    for i in range(3):
        g.emit('ADD', R['k%d' % i], R['k%d' % i], R['RHO'])
    g.emit('MOV', X, R['X0']); g.emit('MOV', R['BASE'], ZERO); g.emit('MOV', R['CNT'], ZERO); g.emit('MOV', R['LAST'], ZERO)
    # ---------------- trail: unrolled blocks of K steps
    g.label('block')
    for k in range(K):
        emit_step()
        g.emit('BLT', X, DELTA, g.target('stub%d' % k))
        g.label('ret%d' % k)
    g.emit('IADDI', R['BASE'], R['BASE'], K)
    g.emit('BLT', R['BASE'], SCAPR, g.target('block'))
    g.label('trail_end')
    g.emit('HALT', 1)                                 # no repeat within the budget
    for k in range(K):
        g.label('stub%d' % k)
        g.emit('IADDI', R['POS'], ZERO, k + 1); g.emit('MOV', R['RET'], g.target('ret%d' % k)); g.emit('JMP', g.target('handler'))

    def extract(bp, mask, dst):
        """dst = field at bit offset R[bp] (10 instructions, 12 operations)."""
        g.emit('SHRV', R['WI'], bp, C8); g.emit('AND', R['OFF'], bp, C255)
        g.emit('LD', R['W0'], R['WI']); g.emit('IADDI', R['WI'], R['WI'], 1); g.emit('LD', R['W1'], R['WI'])
        g.emit('SHRV', R['T1'], R['W0'], R['OFF']); g.emit('ISUB', R['T2'], C256, R['OFF'])
        g.emit('SHLV', R['T2'], R['W1'], R['T2']); g.emit('OR', R['T1'], R['T1'], R['T2']); g.emit('AND', dst, R['T1'], mask)

    def insert(bp, src):
        """OR the field src into the zeroed table at bit offset R[bp] (two read-modify-writes)."""
        g.emit('SHRV', R['WI'], bp, C8); g.emit('AND', R['OFF'], bp, C255)
        g.emit('LD', R['W0'], R['WI']); g.emit('SHLV', R['T1'], src, R['OFF']); g.emit('OR', R['W0'], R['W0'], R['T1'])
        g.emit('ST', R['WI'], R['W0'])
        g.emit('IADDI', R['WI'], R['WI'], 1); g.emit('LD', R['W1'], R['WI']); g.emit('ISUB', R['T2'], C256, R['OFF'])
        g.emit('SHRV', R['T1'], src, R['T2']); g.emit('OR', R['W1'], R['W1'], R['T1']); g.emit('ST', R['WI'], R['W1'])
    # ---------------- DP handler
    g.label('handler')
    g.emit('IADD', R['I'], R['BASE'], R['POS'])
    g.emit('MOV', R['BPV'], ZERO); g.emit('MOV', R['BPG'], GB); g.emit('MOV', R['IDX'], ZERO); g.emit('MOV', R['PIDX'], ZERO)
    g.emit('MOV', R['PVAL'], R['X0']); g.emit('MOV', R['E'], ZERO)
    g.emit('BEQ', R['E'], R['CNT'], g.target('notfound'))
    g.label('scan')
    extract(R['BPV'], MV, R['V']); extract(R['BPG'], MG, R['GV'])
    g.emit('IADD', R['IDX'], R['IDX'], R['GV'])
    g.emit('BEQ', R['V'], X, g.target('found'))
    g.label('scan_nohit')
    g.emit('MOV', R['PIDX'], R['IDX']); g.emit('MOV', R['PVAL'], R['V'])
    g.emit('IADD', R['BPV'], R['BPV'], VBR); g.emit('IADD', R['BPG'], R['BPG'], WGR)
    g.emit('IADDI', R['E'], R['E'], 1); g.emit('BNE', R['E'], R['CNT'], g.target('scan'))
    g.label('notfound')
    g.emit('BEQ', R['CNT'], MCAPR, g.target('fail_overflow'))
    g.label('nf_room')
    g.emit('ISUB', R['GAP'], R['I'], R['LAST'])
    g.emit('BLT', R['GAP'], LIMWG, g.target('gapok'))
    g.label('gap_fail')
    g.emit('HALT', 3)                                 # gap field width exceeded
    g.label('gapok')
    insert(R['BPV'], X); insert(R['BPG'], R['GAP'])
    g.emit('IADDI', R['CNT'], R['CNT'], 1); g.emit('MOV', R['LAST'], R['I']); g.emit('JMP', R['RET'])
    g.label('fail_overflow')
    g.emit('HALT', 2)
    # ---------------- repeat found: entry index IDX = i1, previous stored index PIDX = a with value PVAL
    g.label('found')
    g.emit('ISUB', R['LAM'], R['I'], R['IDX']); g.emit('IADD', R['TB'], R['PIDX'], R['LAM'])
    g.emit('MOV', R['A'], R['PVAL'])
    # second scan: b = largest stored index <= tb, with its value (x_0 if none)
    g.emit('MOV', R['BPV'], ZERO); g.emit('MOV', R['BPG'], GB); g.emit('MOV', R['IDX'], ZERO)
    g.emit('MOV', R['BIDX'], ZERO); g.emit('MOV', R['BVAL'], R['X0']); g.emit('MOV', R['E'], ZERO)
    g.label('scan2')
    extract(R['BPV'], MV, R['V']); extract(R['BPG'], MG, R['GV'])
    g.emit('IADD', R['IDX'], R['IDX'], R['GV'])
    g.emit('BLT', R['TB'], R['IDX'], g.target('scan2done'))
    g.label('scan2_cont')
    g.emit('MOV', R['BIDX'], R['IDX']); g.emit('MOV', R['BVAL'], R['V'])
    g.emit('IADD', R['BPV'], R['BPV'], VBR); g.emit('IADD', R['BPG'], R['BPG'], WGR)
    g.emit('IADDI', R['E'], R['E'], 1); g.emit('BNE', R['E'], R['CNT'], g.target('scan2'))
    g.label('scan2done')
    g.emit('ISUB', R['DIST'], R['TB'], R['BIDX'])
    g.emit('BLT', GPOSR, R['DIST'], g.target('fail_pos'))
    g.label('pos_setup')
    # positioning: X = x_b, DIST steps
    g.emit('MOV', X, R['BVAL']); g.emit('MOV', R['CC'], ZERO)
    g.emit('BEQ', R['CC'], R['DIST'], g.target('posdone'))
    g.label('pos')
    g.emit('MOV', R['RET2'], g.target('posret')); g.emit('JMP', g.target('stepsub'))
    g.label('posret')
    g.emit('IADDI', R['CC'], R['CC'], 1); g.emit('BNE', R['CC'], R['DIST'], g.target('pos'))
    g.label('posdone')
    g.emit('MOV', R['B'], X)
    # lockstep
    g.emit('MOV', R['CC'], ZERO)
    g.label('lock')
    g.emit('MOV', X, R['A']); g.emit('MOV', R['RET2'], g.target('lr1')); g.emit('JMP', g.target('stepsub'))
    g.label('lr1')
    g.emit('MOV', R['FA'], X); g.emit('MOV', X, R['B']); g.emit('MOV', R['RET2'], g.target('lr2')); g.emit('JMP', g.target('stepsub'))
    g.label('lr2')
    g.emit('BEQ', R['FA'], X, g.target('equal'))
    g.label('lr2_cont')
    g.emit('MOV', R['A'], R['FA']); g.emit('MOV', R['B'], X)
    g.emit('IADDI', R['CC'], R['CC'], 1); g.emit('BNE', R['CC'], GR, g.target('lock'))
    g.label('lock_cap')
    g.emit('HALT', 5)                                 # lockstep cap
    g.label('fail_pos')
    g.emit('HALT', 4)                                 # positioning cap
    g.label('equal')
    g.emit('BEQ', R['A'], R['B'], g.target('fail_cycle'))
    g.label('output')
    # output: messages of A and B; fifth root by a left-to-right ladder over the bits of e5
    frc = [0]

    def fifth_root(src, dst):
        g.emit('MOV', R['RR'], ONE); g.emit('MOV', R['BM'], TOPBIT)
        frc[0] += 1
        lab = 'fr%d' % frc[0]
        g.label(lab)
        g.emit('MUL', R['RR'], R['RR'], R['RR']); g.emit('AND', R['TT'], E5R, R['BM'])
        skip = lab + 's'
        g.emit('BEQ', R['TT'], ZERO, g.target(skip))
        g.label(lab + 'b')
        g.emit('MUL', R['RR'], R['RR'], src)
        g.label(skip)
        g.emit('SHRV', R['BM'], R['BM'], ONE); g.emit('BNE', R['BM'], ZERO, g.target(lab))
        g.label(lab + 'e')
        g.emit('MOV', dst, R['RR'])
    g.emit('MOV', R['OUTA'], ZERO)
    for P_ in ('A', 'B'):
        g.emit('ADD', R['WW'], R[P_], R['RHO'])
        fifth_root(R['WW'], R['TT'] if False else R['XA'])            # T = W^e5
        g.emit('ADD', R['XB'], R['XA'], A0R)                          # A = T + A0
        g.emit('MUL', R['M1'], MU5, R['XA']); g.emit('ADD', R['M1'], R['M1'], B0R)    # B = mu5 T + B0
        fifth_root(R['XB'], R['M0']); g.emit('ADD', R['M0'], R['M0'], C00)            # nk = A^e5 - c00
        fifth_root(R['M1'], R['XB']); g.emit('ADD', R['M1'], R['XB'], C01)            # rho = B^e5 - c01
        g.emit('ST', R['OUTA'], R['M0']); g.emit('IADDI', R['OUTA'], R['OUTA'], 1)
        g.emit('ST', R['OUTA'], R['M1']); g.emit('IADDI', R['OUTA'], R['OUTA'], 1)
    g.emit('HALT', 0)
    g.label('fail_cycle')
    g.emit('HALT', 6)
    # step subroutine (one copy)
    g.label('stepsub')
    emit_step()
    g.emit('JMP', R['RET2'])
    # fix the gap-array base and resolve label constants
    gap_base_bit = gap_base_word * 256
    consts_vals = []
    for reg_, val in g.consts:
        if isinstance(val, tuple):
            val = g.labels[val[1]]
        if reg_ == g.regs['GAPBASEBIT']:
            val = gap_base_bit
        consts_vals.append(val)
    tnames = [v[1] for _, v in g.consts if isinstance(v, tuple)]
    assert set(tnames) <= set(pre_targets) or not pre_targets, set(tnames) - set(pre_targets)
    return {'target_names': tnames, 'step_scratch': STEP_SCRATCH, 'code': g.code, 'labels': g.labels, 'regs': g.regs, 'const_regs': [r_ for r_, _ in g.consts], 'const_vals': consts_vals,
            'CBASE': CBASE, 'TABLE_WORDS': TABLE_WORDS, 'words_v': words_v, 'words_g': words_g, 'X0ADDR': X0ADDR, 'L': L, 'outscale': outscale}


def run(prog, rand_words, max_instr=10 ** 9, hits=None):
    """execute; returns (halt code, cost, instructions executed, memory, registers); hits (dict) counts label entries."""
    code = prog['code']
    labat = {v: k for k, v in prog['labels'].items()} if hits is not None else {}
    MEM = {}
    for i, v in enumerate(prog['const_vals']):
        MEM[prog['CBASE'] + i] = v
    R = [0] * 512
    pc = 0; cost = 0; n = 0
    rw = iter(rand_words)
    while True:
        if labat and pc in labat:
            hits[labat[pc]] = hits.get(labat[pc], 0) + 1
        op, a, b, c = code[pc]
        cost += OPS[op]; n += 1
        assert n < max_instr
        pc += 1
        if op == 'ADD':
            R[a] = (R[b] + R[c]) % P
        elif op == 'SUB':
            R[a] = (R[b] - R[c]) % P
        elif op == 'MUL':
            R[a] = R[b] * R[c] % P
        elif op == 'IADD':
            R[a] = (R[b] + R[c]) & M256
        elif op == 'ISUB':
            R[a] = (R[b] - R[c]) & M256
        elif op == 'IADDI':
            R[a] = (R[b] + c) & M256
        elif op == 'MOV':
            R[a] = R[b]
        elif op == 'AND':
            R[a] = R[b] & R[c]
        elif op == 'OR':
            R[a] = R[b] | R[c]
        elif op == 'SHRV':
            R[a] = R[b] >> R[c] if R[c] < 256 else 0
        elif op == 'SHLV':
            R[a] = (R[b] << R[c]) & M256 if R[c] < 256 else 0
        elif op == 'LD':
            R[a] = MEM.get(R[b], 0)
        elif op == 'ST':
            MEM[R[a]] = R[b]
        elif op == 'BLT':
            if R[a] < R[b]:
                pc = R[c]
        elif op == 'BEQ':
            if R[a] == R[b]:
                pc = R[c]
        elif op == 'BNE':
            if R[a] != R[b]:
                pc = R[c]
        elif op == 'JMP':
            pc = R[a]
        elif op == 'RAND':
            R[a] = next(rw)
        elif op == 'HALT':
            return a, cost, n, MEM, R
        else:
            raise ValueError(op)


def static_costs(prog):
    """cost of straight-line regions between labels (for the closed-form ledger)."""
    code, lab = prog['code'], prog['labels']
    def span(l0, l1):
        return sum(OPS[code[i][0]] for i in range(lab[l0], lab[l1]))
    return span


def region_costs(prog):
    """static cost of the listing's regions (label spans), used by the worst-case ledger."""
    code, lab = prog['code'], prog['labels']
    def c(l0, l1):
        return sum(OPS[code[i][0]] for i in range(lab[l0], lab[l1]))
    step_sub = c('stepsub', 'stepsub') + sum(OPS[code[i][0]] for i in range(lab['stepsub'], len(code)))   # the copy + JMP RET2
    rc = {
        'setup_pre': c('start', 'zl'), 'zero_iter': c('zl', 'zl_end'), 'setup_post': c('zl_end', 'block'),
        'block': c('block', 'trail_end'), 'trail_halt': 1, 'stub': c('stub0', 'stub1'),
        'h_pre': c('handler', 'scan'), 'scan_iter': c('scan', 'notfound'), 'scan_hit_part': c('scan', 'scan_nohit'),
        'notfound': c('notfound', 'nf_room') + c('nf_room', 'gap_fail') + c('gapok', 'fail_overflow'),
        'overflow': c('notfound', 'nf_room') + 1,
        'found_pre': c('found', 'scan2'), 'scan2_iter': c('scan2', 'scan2done'), 'scan2_exit_part': c('scan2', 'scan2_cont'),
        'pos_pre': c('scan2done', 'pos_setup') + c('pos_setup', 'pos'),
        'pos_iter': c('pos', 'posdone') + step_sub, 'lock_pre': c('posdone', 'lock'),
        'lock_iter': c('lock', 'lock_cap') + 2 * step_sub, 'equal': c('equal', 'output'), 'step_sub': step_sub,
    }
    return rc


def output_cost(prog):
    """the output segment is deterministic (its branches depend only on the bits of e5): execute it on dummy values."""
    code, lab = prog['code'], prog['labels']
    R = [0] * 512
    for r_, v in zip(prog['const_regs'], prog['const_vals']):
        R[r_] = v
    R[prog['regs']['A']] = 5; R[prog['regs']['B']] = 7
    pc = lab['output']; cost = 0
    while True:
        op, a, b, c = code[pc]; cost += OPS[op]; pc += 1
        if op == 'HALT':
            return cost
        if op == 'ADD': R[a] = (R[b] + R[c]) % P
        elif op == 'MUL': R[a] = R[b] * R[c] % P
        elif op == 'IADDI': R[a] = (R[b] + c) & M256
        elif op == 'MOV': R[a] = R[b]
        elif op == 'AND': R[a] = R[b] & R[c]
        elif op == 'SHRV': R[a] = R[b] >> R[c] if R[c] < 256 else 0
        elif op == 'ST': pass
        elif op == 'BEQ':
            if R[a] == R[b]: pc = R[c]
        elif op == 'BNE':
            if R[a] != R[b]: pc = R[c]
        else: raise ValueError(op)


def worst_case(prog, S, MCAP, G, GPOS, K=15):
    """worst-case cost of one attempt over every control path (all caps charged)."""
    rc = region_costs(prog); out = output_cost(prog)
    blocks = -(-S // K)
    rows = {}
    rows['setup (constants, table zeroing, coins)'] = rc['setup_pre'] + prog['TABLE_WORDS'] * rc['zero_iter'] + rc['setup_post']
    rows['trail: %d blocks x %d' % (blocks, rc['block'])] = blocks * rc['block'] + rc['trail_halt']
    calls = MCAP
    rows['DP handler: %d insertions (stub, preamble, scan of c = 0..MCAP-1 entries, insert)' % calls] =         calls * (rc['stub'] + rc['h_pre'] + rc['notfound']) + rc['scan_iter'] * (MCAP * (MCAP - 1) // 2)
    last_found = rc['found_pre'] + MCAP * rc['scan2_iter'] + rc['pos_pre'] + GPOS * rc['pos_iter'] + rc['lock_pre'] + G * rc['lock_iter'] + rc['equal'] + out
    rows['last DP call: scan of MCAP entries, then the larger of overflow and recovery (second scan, positioning cap, lockstep cap, output)'] =         rc['stub'] + rc['h_pre'] + MCAP * rc['scan_iter'] + max(rc['overflow'], last_found)
    return sum(rows.values()), rows, rc, out


def path_cost(prog, hits, halt):
    """exact cost of an executed path from its label entry counts (every region below is straight-line from its label
    to the next listed label, so cost = sum over regions of entries x region cost)."""
    code, lab = prog['code'], prog['labels']
    order = sorted(lab.items(), key=lambda kv: kv[1])
    pos = [v for _, v in order] + [len(code)]
    cost = 0
    for (name, start), end in zip(order, pos[1:]):
        h = hits.get(name, 0)
        if not h:
            continue
        # a region may exit early only at a branch; charge up to the first taken exit: count instructions until the first
        # branch/jump/halt whose taken target leaves the region (handled by the label entry counts of the next regions)
        seg = 0
        for i in range(start, end):
            seg += OPS[code[i][0]]
        cost += h * seg
    return cost

"""search.py - the one-trail distinguished-point collision search (reference implementation, any map F on [0, N)).

Parameters: Delta (distinguished set D = {v < Delta}), S trail-step cap, MCAP table capacity, G (recovery cap),
d (detection allowance), WG (gap field width in bits).
Trail: x_0 given (index 0, kept as the start word). For i = 1..S: x_i = F(x_{i-1}); if x_i < Delta (DP test:
one comparison, one branch): scan the table (entries in index order: the DP value and the gap to the previous
stored index); a stored value equal to x_i -> repeat detected at i2 = i with i1 = the stored index; else append
(x_i, i - last) if the table holds fewer than MCAP entries and the gap is below 2^WG, otherwise stop (failure).
Recovery (Section 4 of the proof):
  lam = i2 - i1; a = the stored index preceding i1 in the table (0 = the start word x_0 if none); A = x_a.
  target index tb = a + lam; b = the largest stored index <= tb (b >= a); walk B from x_b for tb - b steps
  (capped at GPOS = G + d - 1; above the cap: stop, failure 'pos-cap').
  Lockstep: while F(A) != F(B): A, B = F(A), F(B) (capped at G iterations; above: failure 'lock-cap').
  Output (A, B) if A != B (two distinct points with equal images), else failure 'start-on-cycle'.
Returns (code, pair, counters).
"""


def search(F, x0, Delta, S, MCAP, G, d, WG):
    table = []                 # (value, gap)
    last = 0
    x = x0
    cnt = {'trail_steps': 0, 'dp_hits': 0, 'scan_entries': 0, 'pos_evals': 0, 'lock_iters': 0}
    for i in range(1, S + 1):
        x = F(x)
        cnt['trail_steps'] += 1
        if x < Delta:
            cnt['dp_hits'] += 1
            idx = 0
            hit = None
            prev_idx = 0
            for (v, gap) in table:
                cnt['scan_entries'] += 1
                idx += gap
                if v == x:
                    hit = idx
                    break
                prev_idx = idx
            if hit is not None:
                return recover(F, x0, table, hit, prev_idx, i, G, d, cnt)
            if len(table) >= MCAP:
                return 'table-full', None, cnt
            if i - last >= 1 << WG:
                return 'gap-width', None, cnt
            table.append((x, i - last))
            last = i
    return 'no-repeat', None, cnt


def stored_value(x0, table, index):
    if index == 0:
        return x0
    idx = 0
    for (v, gap) in table:
        idx += gap
        if idx == index:
            return v
    raise KeyError(index)


def recover(F, x0, table, i1, a, i2, G, d, cnt):
    lam = i2 - i1
    A = stored_value(x0, table, a)
    tb = a + lam
    b, idx = 0, 0
    for (v, gap) in table:                       # largest stored index <= tb
        if idx + gap > tb:
            break
        idx += gap
        b = idx
    B = stored_value(x0, table, b)
    dist = tb - b
    if dist > G + d - 1:
        return 'pos-cap', None, cnt
    for _ in range(dist):
        B = F(B); cnt['pos_evals'] += 1
    for _ in range(G):
        FA, FB = F(A), F(B)
        cnt['lock_iters'] += 1
        if FA == FB:
            if A == B:
                return 'start-on-cycle', None, cnt
            cnt['mu_minus_a'] = cnt['lock_iters']
            cnt['pos_dist'] = dist
            return 'ok', (A, B), cnt
        A, B = FA, FB
    return 'lock-cap', None, cnt

def compile_prog(prog, consts):
    lines = ['def F(x):']
    for name, v in consts.items():
        pass
    reg = {}
    for o, d, a, b in prog:
        if o == 'mul':
            lines.append(f'    {d} = {a} * {b} % P')
        elif o == 'add':
            lines.append(f'    {d} = ({a} + {b}) % P')
        elif o == 'alias':
            lines.append('    t0, t1, t2 = n0, n1, n2')
        elif o == 'rename':
            lines.append(f'    {d} = {a}')
    lines.append('    return out')
    env = {'P': P}
    env.update(consts)
    exec('\n'.join(lines), env)
    return env['F']



SEARCH = {"w": 14, "MCAP": 96, "Delta": 6144, "n": 171, "d": 16, "G": 16, "S": 187}
W_BITS = 10
PARAMS = {"Delta": 128, "S": 60, "G": 40, "d": 21, "n": 39}
MCAP_X = 32


def search_experiment(req):
    w, Delta, S, MC, G, d = SEARCH['w'], SEARCH['Delta'], SEARCH['S'], SEARCH['MCAP'], SEARCH['G'], SEARCH['d']
    L, sp, consts, outs = build(30, 0)
    F0 = compile_prog(sp, consts)
    mask = (1 << w) - 1
    out = []
    for t in req['trials']:
        seed = bytes.fromhex(t['seed'])
        rw = [int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), 'little') for j in range(2)]
        rho0 = rw[0] & ((1 << 254) - 1); x0 = rw[1] & mask
        F = lambda x: F0((x + rho0) % P) * outs % P & mask
        code, pair, cnt = search(F, x0, Delta, S, MC, G, d, 2 * w)
        obs = {'outcome_ok': 1 if code == 'ok' else 0, 'trail_steps': cnt['trail_steps'], 'dp_hits': cnt['dp_hits']}
        if code == 'ok':
            ma = L.message((pair[0] + rho0) % P); mb = L.message((pair[1] + rho0) % P)
            a = ma[0].to_bytes(32, 'little') + ma[1].to_bytes(32, 'little')
            b = mb[0].to_bytes(32, 'little') + mb[1].to_bytes(32, 'little')
            out.append({'trial': t['trial'], 'message_a_hex': a.hex(), 'message_b_hex': b.hex(), 'observations': obs})
        else:
            out.append({'trial': t['trial'], 'message_a_hex': None, 'message_b_hex': None, 'observations': obs})
    sys.stdout.write(json.dumps({'schema_version': 1, 'trials': out}, separators=(',', ':')))


def experiment_main():
    req = json.loads(sys.stdin.read())
    if req.get('experiment_id') == 'r30-search-w%d' % SEARCH['w']:
        return search_experiment(req)
    par = PARAMS
    Delta, S, G, d = par['Delta'], par['S'], par['G'], par['d']
    VB = max(1, (Delta - 1).bit_length())
    prog = build_program(Delta, S, MCAP_X, G, G + d - 1, VB, 2 * W_BITS, trunc=W_BITS, digest_trunc=True)
    wc = worst_case(prog, S, MCAP_X, G, G + d - 1)[0]
    out = []
    for t in req['trials']:
        seed = bytes.fromhex(t['seed'])
        rw = [int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), 'little') for j in range(4)]
        code, cost, ni, MEM, R = run(prog, rw, max_instr=10 ** 8)
        if code == 0:
            a = MEM[0].to_bytes(32, 'little') + MEM[1].to_bytes(32, 'little')
            b = MEM[2].to_bytes(32, 'little') + MEM[3].to_bytes(32, 'little')
            out.append({'trial': t['trial'], 'message_a_hex': a.hex(), 'message_b_hex': b.hex(),
                        'observations': {'halt_code': code, 'counted_cost': cost, 'worst_case': wc}})
        else:
            out.append({'trial': t['trial'], 'message_a_hex': None, 'message_b_hex': None,
                        'observations': {'halt_code': code, 'counted_cost': cost, 'worst_case': wc}})
    sys.stdout.write(json.dumps({'schema_version': 1, 'trials': out}, separators=(',', ':')))


if __name__ == '__main__':
    experiment_main()
