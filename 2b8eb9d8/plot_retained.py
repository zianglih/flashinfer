"""Plot mixed fresh/reused candidate versus historical production-equivalent822 baseline."""
import argparse,csv,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
HERE=Path(__file__).resolve().parent
MODELS=[('v3','V3',8),('v41-flash','V41F',4),('kimi-k3','K3',8),('nemo3-ultra','N3U',8)]
MODES=['CuteDSL W4A4','CuteDSL PER-TOKEN','CuteDSL W4A16','CuteDSL MXFP4x8','CuteDSL MXFP8'];TOKENS=[4,8,16,32,64,128,256,512,4096,8192,16384]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--label',required=True);a=p.parse_args()
 source=HERE/'report/cells.csv';rows=list(csv.DictReader(source.open()));out=HERE/'plots';out.mkdir(exist_ok=True)
 lookup={(r['topology'],r['model'],int(r['tokens']),r['backend']):r for r in rows}
 cmap=colors.LinearSegmentedColormap.from_list('red_white_green',['#b2182b','#ffffff','#1a9850']);cmap.set_bad('#e9edf2');norm=colors.TwoSlopeNorm(vmin=-5,vcenter=0,vmax=5)
 manifests=[]
 for topology in ('ep','tp'):
  ordered=[lookup.get((topology,model,t,mode)) for model,_,_ in MODELS for t in TOKENS for mode in MODES]
  matrix=np.array([float(r['speedup_percent']) if r else np.nan for r in ordered]).reshape(44,5)
  fig,ax=plt.subplots(figsize=(10.2,17.5),facecolor='white');fig.subplots_adjust(left=.28,right=.96,top=.90,bottom=.13)
  im=ax.imshow(np.ma.masked_invalid(matrix),cmap=cmap,norm=norm,aspect='auto',interpolation='nearest')
  ax.set_xticks(range(5),[m.removeprefix('CuteDSL ') for m in MODES],fontsize=10);ax.xaxis.tick_top()
  ax.set_yticks(range(44),[f'{t:,}' for _ in MODELS for t in TOKENS],fontsize=9);ax.tick_params(length=0,pad=8)
  for spine in ax.spines.values():spine.set_visible(False)
  for i,(model,label,parallel) in enumerate(MODELS):
   ax.text(-1.45,i*11+5,label+f' {topology.upper()}{parallel}',ha='center',va='center',fontsize=11,weight='bold',color='#253447',clip_on=False)
   if i:ax.axhline(i*11-.5,color='#253447',lw=1.3)
   ax.axhline(i*11+7.5,color='#69778a',lw=.6,linestyle=(0,(3,3)))
  for i in range(44):
   for j in range(5):
    r=ordered[i*5+j];value=matrix[i,j]
    label='N/A' if r is None else f'{value:+.2f}%'+('*' if r['variance_flag']=='True' else '')
    ax.text(j,i,label,ha='center',va='center',fontsize=9,color='#768396' if r is None else 'white' if abs(value)>3.8 else '#17212d')
  fig.text(.04,.974,f'Gathered MoE · {topology.upper()} · retained baseline',fontsize=19,weight='bold',color='#18283c',va='top')
  fig.text(.04,.951,f'{a.label} · B300 / strict CUPTI · all supported modes',fontsize=10,color='#526174',va='top')
  fig.text(.04,.934,'Baseline measured 326c4a79; production-equivalent to 82254e20. Historical timing reused.',fontsize=9.4,color='#526174',va='top')
  cbax=fig.add_axes([.30,.082,.62,.012]);cb=fig.colorbar(im,cax=cbax,orientation='horizontal',extend='both');cb.set_ticks([-5,-2.5,0,2.5,5],labels=['−5%','−2.5%','0%','+2.5%','+5%']);cb.outline.set_visible(False)
  fig.text(.04,.059,'Positive: candidate faster. Red/green colours saturate at ±5%; every label is unclipped.',fontsize=9,color='#37465a')
  fig.text(.04,.042,'* Either baseline/candidate repeat spread >1%. Gray: unsupported. Tokens1–2 omitted.',fontsize=9,color='#37465a')
  fig.text(.04,.025,'100 × (historical two-pass baseline / current two-pass candidate − 1); not a fresh paired comparison.',fontsize=8.9,color='#37465a')
  outputs={}
  for extension in ('png','svg'):
   path=out/f'retained-speedup-{topology}.{extension}';fig.savefig(path,dpi=180,facecolor='white');outputs[path.name]=sha(path)
  plt.close(fig);manifests.append(dict(topology=topology,rows=44,columns=5,measured=sum(r is not None for r in ordered),negative=sum(float(r['speedup_percent'])<0 for r in ordered if r),outputs=outputs,source_sha256=sha(source)))
 (out/'retained-plot-manifest.json').write_text(json.dumps(dict(script_sha256=sha(__file__),label=a.label,plots=manifests),indent=2)+'\n')
if __name__=='__main__':main()
