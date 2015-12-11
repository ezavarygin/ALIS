import os
import datetime
import almsgs
from alutils import getreason
msgs=almsgs.msgs()

def print_model(diff, mp, thresh, verbose=2, funcarray=[None, None, None]):
    function=funcarray[0]
    funccall=funcarray[1]
    funcinst=funcarray[2]
    level=0
    convstring = ""
    donecv, donesh, donezl = [], [], []
    lastemab=""
    for i in range(len(mp['mtyp'])):
        #if errs is not None and mp['emab'][i] == "cv": continue
        mtyp = mp['mtyp'][i]
        if mp['emab'][i] != lastemab:
            if   mp['emab'][i]=="em": aetag = "emission"
            elif mp['emab'][i]=="ab": aetag = "absorption"
            elif mp['emab'][i]=="cv": aetag = "Convolution"
            elif mp['emab'][i]=="sh": aetag = "Shift"
            elif mp['emab'][i]=="zl": aetag = "zerolevel"
            convstring += "#"+aetag+"\n"
            lastemab = mp['emab'][i]
        funcinst[mtyp]._keywd = mp['mkey'][i]
        outstr, cnvstr, level = funccall[mtyp].parout(funcinst[mtyp], diff, mp, i, level, conv=thresh)
        if outstr in donecv or outstr in donesh or outstr in donezl: continue
        if mp['emab'][i] == "cv": donecv.append(outstr) # Make sure we don't print convolution more than once.
        if mp['emab'][i] == "sh": donesh.append(outstr) # Make sure we don't print shifts more than once.
        if mp['emab'][i] == "zl": donezl.append(outstr) # Make sure we don't print zerolevel more than once.
        convstring += cnvstr
    return convstring

def save_convtest(slf,diff,thresh,info,printout=True,extratxt=["",""]):
    """
    Save the details of what parameters have converged.
    """
    msgs.info("Saving the best-fitting model parameters", verbose=slf._argflag['out']['verbose'])
    filename = extratxt[0]+slf._argflag['run']['modname']+'.conv'+extratxt[1]
    prestring = "#\n#  Generated by ALIS on {0:s}\n#\n".format(datetime.datetime.now().strftime("%d/%m/%y at %H:%M:%S"))
    prestring += "#   Running Time (hrs)  = {0:f}\n".format(info[0])
    prestring += "#   Initial Chi-Squared = {0:f}\n".format(slf._chisq_init)
    prestring += "#   Bestfit Chi-Squared = {0:f}\n".format(info[1])
    prestring += "#   Degrees-of-Freedom  = {0:d}\n".format(info[2])
    prestring += "#   Num. of Iterations  = {0:d}\n".format(info[3])
    prestring += "#   Convergence Reason  = {0:s}\n".format(getreason(info[4],verbose=slf._argflag['out']['verbose']))
    prestring += "\n"
    inputmodl = "#\n"
    for i in range(len(slf._parlines)):
        prestring += slf._parlines[i]
        inputmodl += "#   "+slf._parlines[i]
    prestring +="\ndata read\n"
    inputmodl += "#   data read\n"
    msgs.bug("INCLUDE THE BEST-FIT FWHM HERE --- PLACE THE ERROR BELOW", verbose=slf._argflag['out']['verbose'])
    for i in range(len(slf._datlines)):
        prestring += slf._datlines[i]
        inputmodl += "#   "+slf._datlines[i]
    prestring +="data end\n"
    inputmodl += "#   data end\n"
    prestring +="\nmodel read\n"
    inputmodl += "#   model read\n"
    modcomlin=[]
    modcomind=[]
    tconvstring=''
    for i in range(len(slf._modlines)):
        if slf._modlines[i].split()[0] in ["fix", "lim"]: tconvstring += slf._modlines[i].replace('\t',' ')
        if slf._modlines[i].lstrip()[0] == '#':
            modcomlin.append(slf._modlines[i].rstrip('\n'))
            modcomind.append(i)
        inputmodl += "#   "+slf._modlines[i]
    convstring = print_model(diff,slf._modpass,thresh,verbose=slf._argflag['out']['verbose'],funcarray=slf._funcarray)
#	if printout and slf._argflag['out']['verbose'] != -1:
#		print "\n####################################################"
#		print convstring
#		print "####################################################\n"
    # Reinsert the comments at the original locations
    cnvstrspl = (tconvstring+convstring).split('\n')
    for i in range(len(modcomlin)): cnvstrspl.insert(modcomind[i],modcomlin[i])
    convstring = '\n'.join(cnvstrspl)
    # Include an end tag for the model
    convstring += "model end\n"
    inputmodl += "#   model end\n#\n\n"
    if slf._argflag['out']['overwrite']: ans='y'
    else: ans=''
    if os.path.exists(filename):
        while ans != 'y' and ans != 'n' and ans !='r':
            msgs.warn("File %s exists!" % (filename), verbose=slf._argflag['out']['verbose'])
            ans = raw_input(msgs.input()+"Overwrite? (y/n) or rename? (r) - ")
            if ans == 'r':
                fileend=raw_input(msgs.input()+"Enter new filename - ")
                filename = fileend
                if os.path.exists(filename): ans = ''
    if ans != 'n':
        infile = open(filename,"w")
        infile.write(prestring)
        infile.write(convstring+"\n")
        infile.write("\n###################################################")
        infile.write("\n#                                                 #")
        infile.write("\n#          HERE IS A COPY OF THE INPUT MODEL      #")
        infile.write("\n#                                                 #")
        infile.write("\n###################################################\n")
        infile.write(inputmodl)
        infile.close()
        msgs.info("Saved output file successfully:"+msgs.newline()+filename, verbose=slf._argflag['out']['verbose'])

