import main.modules.pe as pe
import main.modules.canslim as cs 
import main.modules.mx4 as m 
import main.common.const as const

helper_PE = pe.PEHelper()
helper_cs = cs.CanslimHelper()
helper_mx = m.Mx4Helper()

# Lấy theo quý
listPAT = [1516.13,2006.73,2298.4,1869.13,1856.73,2198.81,1977.975,1946.858]

print(helper_PE.GetDataPoints(listPAT, 2, const.END_MODE))
print(helper_PE.ForecastStockPrices(helper_PE.GetDataPoints(listPAT, 2, const.END_MODE), 2089955445.00, 19.13))

# Lấy theo quý
sales = [1250301, 708890 , 2156092 , 1661313 , 1545623 , 1970493 , 1597772 , 992684 , 797173, 1115257]
eps = [4639.00,2229.00, 3524 , 3276 , 4655 , 6274 , 4531 , 3335 , 1760,  840]

print(helper_cs.CalListCanslimScores(sales, eps))
print(helper_cs.EvaluateCanslimScore(helper_cs.CalListCanslimScores(sales, eps)[0]))

# Lấy theo năm
sales = [39531469,42658611,23213537,27716960,29830401,35657263,44009528]
eps = [4641.00,5904.00,4518.00,4797.00,4744.00,5065.00,5252.00]
bvps = [24917.00,24932.00,24076.00,24764.00,23731.00,23599.00,23111.00]
opc = [4311658.00,1988184.00,3588320.00,3898750.00,6339679.00,5839694.00,5053832.00,6799289.00,11448075,13238376]
ld = [955531,660956,530946,492618,763945,2518850,1773117]
pat = [1990643,2931531,2620179,3135350,3538008,4337412,5310109]
assets = [29833262,24999677,29757067,33394164,41734323,53697941,51650404]
equity = [11448075,13238376,14774971,16799289,18605667,21417985,25356125]

data = m.Data4M(sales,eps,bvps,opc,ld,pat,assets,equity)
print(helper_mx.GetDataPoints(data,2).Get())
print(helper_mx.CalList4MScores(helper_mx.GetDataPoints(data,2)))
