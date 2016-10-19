# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import openwrt_router
import qcom_akronite_nand
import qcom_akronite_nor
import qcom_dakota_nor
import qcom_mips
import marvell

def board(model, **kwargs):
    '''
    Depending on the given model, return an object of the appropriate class type.

    Different boards are flashed with different commands, have 
    different memory addresses, and must be handled differently.
    '''
    if model in ("db120", "ap135", "ap143", "ap147", "ap152", "ap151",
                 "ap151-16M", "ap143", "ap152-8M", "tew-823dru"):
        return qcom_mips.QcomMipsRouter(model, **kwargs)

    if model in ("ipq8066", "db149", "ap145", "ap148", "ap148-osprey",
                 "ap148-beeliner", "ap160-1", "ap160-2", "ap161"):
        return qcom_akronite_nand.QcomAkroniteRouterNAND(model, **kwargs)

    if model in ("ap148-nor"):
        return qcom_akronite_nor.QcomAkroniteRouterNOR(model, **kwargs)

    if model in ("dk01-nor"):
        return qcom_dakota_nor.QcomDakotaRouterNOR(model, **kwargs)

    if model in ("wrt3200acm"):
        return marvell.WRT3200ACM(model, **kwargs)

    # Default for all other models
    print("\nWARNING: Unknown board model '%s'." % model)
    print("Please check spelling, or write an appropriate class "
          "to handle that kind of board.")
    return openwrt_router.OpenWrtRouter(model, **kwargs)
