#!/usr/bin/python

import builtins
import keyword

from wx import stc

from const.menu import MI
from const.common import LOREM_IPSUM


#NOTE, Consolas, nice font
FACES = {
    'times': 'Times New Roman',
    'mono' : 'Courier New',
    'helv' : 'Courier New',
    'other': 'Consolas',

    'size' : 10,  # Editor
    'size2':  8,  # Margin, linenumbers
    'size3':  8,  # Calltips
}

#TODO, review 'LANG' and 'LANG_WILDCARDS' definitions
# language definitions
#    0:lexer (id)            1:lng_typ     2:lng_nam       3:extension(s)         4:lng_mni (id)
LANG = (
    (stc.STC_LEX_BASH,       'shell',      'Bash/Shell',   'csh|ksh|sh|zsh',      MI['LNG_BASH']),
    (stc.STC_LEX_BATCH,      'batch',      'Batch/CMD',    'bat|cmd',             MI['LNG_BATCH']),
    (stc.STC_LEX_CONF,       'config',     'Config',       'cfg|conf|ini|rc',     MI['LNG_CONF']),        # apache: conf
    (stc.STC_LEX_CPP,        'cpp',        'C/C++',        'c|cpp|cxx|h|hpp|hxx', MI['LNG_CPP']),
    (stc.STC_LEX_CSS,        'css',        'CSS',          'css',                 MI['LNG_CSS']),
    (stc.STC_LEX_HTML,       'html',       'HTML',         'html|htm',            MI['LNG_HTML']),
    (stc.STC_LEX_MARKDOWN,   'markdown',   'Markdown',     'md',                  MI['LNG_MARKDOWN']),
    (stc.STC_LEX_PASCAL,     'pascal',     'Pascal',       'pas|pp|inc',          MI['LNG_PASCAL']),
    (stc.STC_LEX_PERL,       'perl',       'Perl',         'pl|pm|pod',           MI['LNG_PERL']),
    (stc.STC_LEX_PHPSCRIPT,  'php',        'PHP',          'php',                 MI['LNG_PHPSCRIPT']),
    (stc.STC_LEX_POWERSHELL, 'powershell', 'PowerShell',   'ps1',                 MI['LNG_POWERSHELL']),
    (stc.STC_LEX_PROPERTIES, 'properties', 'Properties',   'properties',          MI['LNG_PROPERTIES']),
    (stc.STC_LEX_PYTHON,     'python',     'Python',       'py|pyw',              MI['LNG_PYTHON']),
    (stc.STC_LEX_RUBY,       'ruby',       'Ruby',         'rb',                  MI['LNG_RUBY']),
    (stc.STC_LEX_SQL,        'sql',        'SQL/(PL/SQL)', 'pls|pks|pkb|pck|sql', MI['LNG_SQL']),
    (stc.STC_LEX_TCL,        'tcl',        'TCL',          'tcl',                 MI['LNG_TCL']),
    (stc.STC_LEX_XML,        'xml',        'XML',          'xml',                 MI['LNG_XML']),
    (stc.STC_LEX_YAML,       'yaml',       'YAML',         'yaml|yml',            MI['LNG_YAML']),
    (stc.STC_LEX_NULL,       'text',       'Plain Text',   'txt',                 MI['LNG_NULL']),
)

################################################################################
#TODO, extra language definitions
# 'Apache Config', 'Awk', 'C#', 'Diff', 'Java', 'JavaScript', 'JSON', 'Registry'
################################################################################


#DONE, integrate with 'language definitions' above...
def create_wildcards():
    spec = ''
    for lng in LANG:
        ext1 = '*.' + lng[3].replace('|', ',*.')
        ext2 = ext1.replace(',', ';')
        spec = spec + '\n' + lng[2] + ' files (' + ext1 + ')|' + ext2 + '|'
    spec = '\nAll files (*.*)|*.*|' + spec[:-1]  # strip last '|'
    return spec

LANG_WILDCARDS = create_wildcards()

# LANG_WILDCARDS = """
#     All files (*.*)|*.*|
#     Bash/Shell files (*.csh,*.ksh,*.sh,*.zsh)|*.csh;*.ksh;*.sh;*.zsh|
#     Batch/CMD files (*.bat,*.cmd)|*.bat;*.cmd|
#     Config files (*.cfg,*.conf,*.ini,*.rc)|*.cfg;*.conf;*.ini;*.rc|
#     C/C++ files (*.c,*.cpp,*.cxx,*.h,*.hpp,*.hxx)|*.c;*.cpp;*.cxx;*.h;*.hpp;*.hxx|
#     CSS files (*.css)|*.css|
#     HTML files (*.html,*.htm)|*.html;*.htm|
#     Markdown files (*.md)|*.md|
#     Pascal files (*.pas,*.pp,*.inc)|*.pas;*.pp;*.inc|
#     Perl files (*.pl,*.pm,*.pod)|*.pl;*.pm;*.pod;*.cgi|
#     PHP files (*.php)|*.php|
#     PowerShell files (*.ps1)|*.ps1|
#     Properties files (*.properties)|*.properties|
#     Python files (*.py,*.pyw)|*.py;*.pyw|
#     Ruby files (*.rb)|*.rb|
#     SQL/(PL/SQL) files (*.pls,*.pks,*.pkb,*.pck,*.sql)|*.pls;*.pks;*.pkb;*.pck;*.sql|
#     TCL files (*.tcl)|*.tcl|
#     XML files (*.xml)|*.xml|
#     YAML files (*.yaml,*.yml)|*.yaml;*.yml|
#     Plain Text files (*.txt)|*.txt""".replace(rs_(4, ' '), '')


#NOTE, extension candidates
#NOTE, see also D:\Dev\Python27\Lib\site-packages\wx-2.8-msw-unicode\wx\tools\Editra\src\syntax
# csv
# ctl,dat,bad,dsc   oracle: sqlldr control, data, bad, discard file
# dtd
# diff
# dot               graphviz
# g                 grammar
# ini
# java
# js                javascript
# json
# ora               oracle: init, listener, sqlnet, tnsnames, ...
# par               oracle: imp/exp(dp) parfile
# rst               reStructuredText
# vb,vbs            visual basic

#INFO, Valid file extensions include ‘.yml’, ‘.yaml’, ‘.json’, or no file extension.
#INFO, URL=https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#organizing-host-and-group-variables
#INFO, URL=https://docs.ansible.com/ansible/latest/reference_appendices/special_variables.html#special-variables
# j2                          Jinja2
# fact,json,toml,yaml,yml     ansible


#TODO, finish keywords
# keywords per lexer
#        0:label              1:set (id)              2:keywords
LANG_KWRD = {
    stc.STC_LEX_BASH: (
        ('Keywords', 0,
        """
        alias bg bind break builtin case cd command compgen complete continue declare dirs disown
        do done echo elif else enable esac eval exec exit export fc fg fi for function getopts
        hash help history if in jobs kill let local logout popd printf pushd pwd read readonly
        return select set shift shopt source suspend test then times trap type typeset ulimit
        umask unalias unset until wait while
        """),
    ),
    stc.STC_LEX_BATCH: (
        ('Internal Commands', 0,
        """
        assoc break call cd chcp chdir cls color copy date del dir dpath echo else endlocal erase
        exist exit for ftype goto if keys md mkdir mklink move not path pause popd prompt pushd
        rd rem ren rename rmdir set setlocal shift start time title type ver verify vol
        """),
        ('External Commands', 1,
        """
        arp at attrib bcdboot bcdedit bitsadmin cacls certreq certutil change chkdsk chkntfs
        choice cipher cleanmgr clip cmd cmdkey comp compact convert defrag diskcomp diskcopy
        diskpart doskey driverquery eventcreate expand explorer fc find findstr fltmc forfiles
        format fsutil ftp getmac gpresult gpupdate help hostname icacls iexpress ipconfig label
        lodctr logman logoff makecab mode more mountvol msg msiexec msinfo32 mstsc nbtstat net
        netsh netstat nltest nslookup openfiles pathping perfmon ping powercfg print qappsrv
        qprocess quser qwinsta rasdial rasphone recover reg regedit regini regsvr32 replace reset
        robocopy route run runas rundll32 sc schtasks setspn setx sfc shutdown sleep slmgr sort
        start strings subst systeminfo takeown taskkill tasklist timeout touch tracert tree
        tsdiscon tskill typeperf tzutil vssadmin w32tm waitfor wbadmin wecutil wevtutil where
        whoami winrm winrs wmic wuauclt wusa xcopy
        """),
    ),
    stc.STC_LEX_CONF: (
        ('Directives', 0,
        """
        authnprovideralias authzprovideralias directory directorymatch else elseif files filesmatch
        if ifdefine ifdirective iffile ifmodule ifsection ifversion limit limitexcept location
        locationmatch macro mdomainset proxy proxymatch requireall requireany requirenone
        virtualhost acceptfilter acceptpathinfo accessfilename action addalt addaltbyencoding
        addaltbytype addcharset adddefaultcharset adddescription addencoding addhandler addicon
        addiconbyencoding addiconbytype addinputfilter addlanguage addmoduleinfo addoutputfilter
        addoutputfilterbytype addtype alias aliasmatch allow allowconnect allowencodedslashes
        allowmethods allowoverride allowoverridelist anonymous anonymous_logemail
        anonymous_mustgiveemail anonymous_nouserid anonymous_verifyemail asyncrequestworkerfactor
        authbasicauthoritative authbasicfake authbasicprovider authbasicusedigestalgorithm
        authdbduserpwquery authdbduserrealmquery authdbmgroupfile authdbmtype authdbmuserfile
        authdigestalgorithm authdigestdomain authdigestnoncelifetime authdigestprovider
        authdigestqop authdigestshmemsize authformauthoritative authformbody authformdisablenostore
        authformfakebasicauth authformlocation authformloginrequiredlocation
        authformloginsuccesslocation authformlogoutlocation authformmethod authformmimetype
        authformpassword authformprovider authformsitepassphrase authformsize authformusername
        authgroupfile authldapauthorizeprefix authldapbindauthoritative authldapbinddn
        authldapbindpassword authldapcharsetconfig authldapcompareasuser authldapcomparednonserver
        authldapdereferencealiases authldapgroupattribute authldapgroupattributeisdn
        authldapinitialbindasuser authldapinitialbindpattern authldapmaxsubgroupdepth
        authldapremoteuserattribute authldapremoteuserisdn authldapsearchasuser
        authldapsubgroupattribute authldapsubgroupclass authldapurl authmerging authname
        authncachecontext authncacheenable authncacheprovidefor authncachesocache authncachetimeout
        authnzfcgicheckauthnprovider authnzfcgidefineprovider authtype authuserfile
        authzdbdlogintoreferer authzdbdquery authzdbdredirectquery authzdbmtype
        authzsendforbiddenonfailure balancergrowth balancerinherit balancermember balancerpersist
        brotlialteretag brotlicompressionmaxinputblock brotlicompressionquality
        brotlicompressionwindow brotlifilternote browsermatch browsermatchnocase bufferedlogs
        buffersize cachedefaultexpire cachedetailheader cachedirlength cachedirlevels cachedisable
        cacheenable cachefile cacheheader cacheignorecachecontrol cacheignoreheaders
        cacheignorenolastmod cacheignorequerystring cacheignoreurlsessionidentifiers cachekeybaseurl
        cachelastmodifiedfactor cachelock cachelockmaxage cachelockpath cachemaxexpire
        cachemaxfilesize cacheminexpire cacheminfilesize cachenegotiateddocs cachequickhandler
        cachereadsize cachereadtime cacheroot cachesocache cachesocachemaxsize cachesocachemaxtime
        cachesocachemintime cachesocachereadsize cachesocachereadtime cachestaleonerror
        cachestoreexpired cachestorenostore cachestoreprivate cgidscripttimeout cgimapextension
        cgipassauth cgivar charsetdefault charsetoptions charsetsourceenc checkcaseonly
        checkspelling chrootdir contentdigest cookiedomain cookieexpires cookiename cookiestyle
        cookietracking coredumpdirectory customlog dav davdepthinfinity davgenericlockdb davlockdb
        davmintimeout dbdexptime dbdinitsql dbdkeep dbdmax dbdmin dbdparams dbdpersist dbdpreparesql
        dbdriver defaulticon defaultlanguage defaultruntimedir defaulttype define deflatebuffersize
        deflatecompressionlevel deflatefilternote deflateinflatelimitrequestbody
        deflateinflateratioburst deflateinflateratiolimit deflatememlevel deflatewindowsize deny
        directorycheckhandler directoryindex directoryindexredirect directoryslash documentroot
        dtraceprivileges dumpioinput dumpiooutput enableexceptionhook enablemmap enablesendfile
        error errordocument errorlog errorlogformat example expiresactive expiresbytype
        expiresdefault extendedstatus extfilterdefine extfilteroptions fallbackresource fileetag
        filterchain filterdeclare filterprotocol filterprovider filtertrace forcelanguagepriority
        forcetype forensiclog globallog gprofdir gracefulshutdowntimeout group h2copyfiles h2direct
        h2earlyhints h2maxsessionstreams h2maxworkeridleseconds h2maxworkers h2minworkers
        h2moderntlsonly h2push h2pushdiarysize h2pushpriority h2pushresource h2serializeheaders
        h2streammaxmemsize h2tlscooldownsecs h2tlswarmupsize h2upgrade h2windowsize header
        headername heartbeataddress heartbeatlisten heartbeatmaxservers heartbeatstorage
        heartbeatstorage hostnamelookups httpprotocoloptions identitycheck identitychecktimeout
        imapbase imapdefault imapmenu include includeoptional indexheadinsert indexignore
        indexignorereset indexoptions indexorderdefault indexstylesheet inputsed
        isapiappendlogtoerrors isapiappendlogtoquery isapicachefile isapifakeasync
        isapilognotsupported isapireadaheadbuffer keepalive keepalivetimeout keptbodysize
        languagepriority ldapcacheentries ldapcachettl ldapconnectionpoolttl ldapconnectiontimeout
        ldaplibrarydebug ldapopcacheentries ldapopcachettl ldapreferralhoplimit ldapreferrals
        ldapretries ldapretrydelay ldapsharedcachefile ldapsharedcachesize ldaptimeout
        ldaptrustedclientcert ldaptrustedglobalcert ldaptrustedmode ldapverifyservercert
        limitinternalrecursion limitrequestbody limitrequestfields limitrequestfieldsize
        limitrequestline limitxmlrequestbody listen listenbacklog listencoresbucketsratio loadfile
        loadmodule logformat logiotrackttfb loglevel logmessage luaauthzprovider luacodecache
        luahookaccesschecker luahookauthchecker luahookcheckuserid luahookfixups luahookinsertfilter
        luahooklog luahookmaptostorage luahooktranslatename luahooktypechecker luainherit
        luainputfilter luamaphandler luaoutputfilter luapackagecpath luapackagepath luaquickhandler
        luaroot luascope maxconnectionsperchild maxkeepaliverequests maxmemfree maxrangeoverlaps
        maxrangereversals maxranges maxrequestworkers maxspareservers maxsparethreads maxthreads
        mdbaseserver mdcachallenges mdcertificateagreement mdcertificateauthority
        mdcertificateprotocol mddrivemode mdhttpproxy mdmember mdmembers mdmuststaple mdnotifycmd
        mdomain mdportmap mdprivatekeys mdrenewwindow mdrequirehttps mdstoredir memcacheconnttl
        mergetrailers metadir metafiles metasuffix mimemagicfile minspareservers minsparethreads
        mmapfile modemstandard modmimeusepathinfo multiviewsmatch mutex namevirtualhost noproxy
        nwssltrustedcerts nwsslupgradeable options order outputsed passenv pidfile privilegesmode
        protocol protocolecho protocols protocolshonororder proxyaddheaders proxybadheader
        proxyblock proxydomain proxyerroroverride proxyexpressdbmfile proxyexpressdbmtype
        proxyexpressenable proxyfcgibackendtype proxyfcgisetenvif proxyftpdircharset
        proxyftpescapewildcards proxyftplistonwildcard proxyhcexpr proxyhctemplate proxyhctpsize
        proxyhtmlbufsize proxyhtmlcharsetout proxyhtmldoctype proxyhtmlenable proxyhtmlevents
        proxyhtmlextended proxyhtmlfixups proxyhtmlinterp proxyhtmllinks proxyhtmlmeta
        proxyhtmlstripcomments proxyhtmlurlmap proxyiobuffersize proxymaxforwards proxypass
        proxypassinherit proxypassinterpolateenv proxypassmatch proxypassreverse
        proxypassreversecookiedomain proxypassreversecookiepath proxypreservehost
        proxyreceivebuffersize proxyremote proxyremotematch proxyrequests proxyscgiinternalredirect
        proxyscgisendfile proxyset proxysourceaddress proxystatus proxytimeout proxyvia
        qualifyredirecturl readmename receivebuffersize redirect redirectmatch redirectpermanent
        redirecttemp reflectorheader regexdefaultoptions registerhttpmethod remoteipheader
        remoteipinternalproxy remoteipinternalproxylist remoteipproxiesheader remoteipproxyprotocol
        remoteipproxyprotocolexceptions remoteiptrustedproxy remoteiptrustedproxylist removecharset
        removeencoding removehandler removeinputfilter removelanguage removeoutputfilter removetype
        requestheader requestreadtimeout require rewritebase rewritecond rewriteengine rewritemap
        rewriteoptions rewriterule rlimitcpu rlimitmem rlimitnproc satisfy scoreboardfile script
        scriptalias scriptaliasmatch scriptinterpretersource scriptlog scriptlogbuffer
        scriptloglength scriptsock securelisten seerequesttail sendbuffersize serveradmin
        serveralias serverlimit servername serverpath serverroot serversignature servertokens
        session sessioncookiename sessioncookiename2 sessioncookieremove sessioncryptocipher
        sessioncryptodriver sessioncryptopassphrase sessioncryptopassphrasefile sessiondbdcookiename
        sessiondbdcookiename2 sessiondbdcookieremove sessiondbddeletelabel sessiondbdinsertlabel
        sessiondbdperuser sessiondbdselectlabel sessiondbdupdatelabel sessionenv sessionexclude
        sessionheader sessioninclude sessionmaxage setenv setenvif setenvifexpr setenvifnocase
        sethandler setinputfilter setoutputfilter ssiendtag ssierrormsg ssietag ssilastmodified
        ssilegacyexprparser ssistarttag ssitimeformat ssiundefinedecho sslcacertificatefile
        sslcacertificatepath sslcadnrequestfile sslcadnrequestpath sslcarevocationcheck
        sslcarevocationfile sslcarevocationpath sslcertificatechainfile sslcertificatefile
        sslcertificatekeyfile sslciphersuite sslcompression sslcryptodevice sslengine sslfips
        sslhonorcipherorder sslinsecurerenegotiation sslocspdefaultresponder sslocspenable
        sslocspnoverify sslocspoverrideresponder sslocspproxyurl sslocsprespondercertificatefile
        sslocsprespondertimeout sslocspresponsemaxage sslocspresponsetimeskew sslocspuserequestnonce
        sslopensslconfcmd ssloptions sslpassphrasedialog sslprotocol sslproxycacertificatefile
        sslproxycacertificatepath sslproxycarevocationcheck sslproxycarevocationfile
        sslproxycarevocationpath sslproxycheckpeercn sslproxycheckpeerexpire sslproxycheckpeername
        sslproxyciphersuite sslproxyengine sslproxymachinecertificatechainfile
        sslproxymachinecertificatefile sslproxymachinecertificatepath sslproxyprotocol
        sslproxyverify sslproxyverifydepth sslrandomseed sslrenegbuffersize sslrequire sslrequiressl
        sslsessioncache sslsessioncachetimeout sslsessionticketkeyfile sslsessiontickets
        sslsrpunknownuserseed sslsrpverifierfile sslstaplingcache sslstaplingerrorcachetimeout
        sslstaplingfaketrylater sslstaplingforceurl sslstaplingrespondertimeout
        sslstaplingresponsemaxage sslstaplingresponsetimeskew sslstaplingreturnrespondererrors
        sslstaplingstandardcachetimeout sslstrictsnivhostcheck sslusername sslusestapling
        sslverifyclient sslverifydepth startservers startthreads substitute substituteinheritbefore
        substitutemaxlinelength suexec suexecusergroup threadlimit threadsperchild threadstacksize
        timeout traceenable transferlog typesconfig undefine undefmacro unsetenv use
        usecanonicalname usecanonicalphysicalport user userdir vhostcgimode vhostcgiprivs vhostgroup
        vhostprivs vhostsecure vhostuser virtualdocumentroot virtualdocumentrootip
        virtualscriptalias virtualscriptaliasip watchdoginterval xbithack xml2encalias
        xml2encdefault xml2startparse
        """),
        ('Parameters', 1, ''),
    ),
    stc.STC_LEX_CPP: (
        ('Primary keywords and identifiers', 0,
        """
        alignas alignof and and_eq asm atomic_cancel atomic_commit atomic_noexcept auto bitand
        bitor bool break case catch char char16_t char32_t class co_await co_return co_yield
        compl concept const const_cast constexpr continue decltype default define defined
        delete do double dynamic_cast elif else endif enum error explicit export extern false
        float for friend goto if ifdef ifndef import include inline int line long module
        mutable namespace new noexcept not not_eq nullptr operator or or_eq pragma private
        protected public register reinterpret_cast requires return short signed sizeof static
        static_assert static_cast struct switch synchronized template this thread_local throw
        true try typedef typeid typename undef union unsigned using virtual void volatile
        wchar_t while xor xor_eq
        """),
        ('Secondary keywords and identifiers', 1, ''),
        ('Documentation comment keywords', 2, ''),
        ('Global classes and typedefs', 3, ''),
        ('Preprocessor definitions', 4, ''),
        ('Task marker and error marker keywords', 5, ''),
    ),
    stc.STC_LEX_CSS: (
        ('CSS1 Properties', 0, ''),
        ('Pseudo-classes', 1, ''),
        ('CSS2 Properties', 2, ''),
        ('CSS3 Properties', 3, ''),
        ('Pseudo-elements', 4, ''),
        ('Browser-Specific CSS Properties', 5, ''),
        ('Browser-Specific Pseudo-classes', 6, ''),
        ('Browser-Specific Pseudo-elements', 7, ''),
    ),
    stc.STC_LEX_HTML: (
        ('HTML elements and attributes', 0, ''),
        ('JavaScript keywords', 1, ''),
        ('VBScript keywords', 2, ''),
        ('Python keywords', 3, ''),
        ('PHP keywords', 4, ''),
        ('SGML and DTD keywords', 5, ''),
    ),
    stc.STC_LEX_MARKDOWN: (),
    stc.STC_LEX_PASCAL: (
        ('Keywords', 0,
        """
        and array as asm begin break case class const constructor continue destructor dispose
        div do downto else end except exit exports false file finalization finally for function
        goto if implementation in inherited initialization inline interface is label library mod
        new nil not object of on on operator or out packed procedure program property raise
        record repeat self set shl shr string then threadvar to true try type unit until uses
        var while with xor
        """),
    ),
    stc.STC_LEX_PERL: (
        ('Keywords', 0,
        """
        AUTOLOAD BEGIN CHECK DESTROY END INIT UNITCHECK __DATA__ __END__ __FILE__ __LINE__
        __PACKAGE__ __SUB__ abs accept alarm and atan2 bind binmode bless break caller chdir
        chmod chomp chop chown chr chroot close closedir cmp connect continue cos crypt dbmclose
        dbmopen default defined delete die do dump each else elseif elsif endgrent endhostent
        endnetent endprotoent endpwent endservent eof eq eval evalbytes exec exists exit exp fc
        fcntl fileno flock for foreach fork format formline ge getc getgrent getgrgid getgrnam
        gethostbyaddr gethostbyname gethostent getlogin getnetbyaddr getnetbyname getnetent
        getpeername getpgrp getppid getpriority getprotobyname getprotobynumber getprotoent
        getpwent getpwnam getpwuid getservbyname getservbyport getservent getsockname getsockopt
        given glob gmtime goto grep gt hex if import index int ioctl join keys kill last lc
        lcfirst le length link listen local localtime lock log lstat lt m map mkdir msgctl
        msgget msgrcv msgsnd my ne next no not oct open opendir or ord our pack package pipe pop
        pos print printf prototype push q qq qr quotemeta qw qx rand read readdir readline
        readlink readpipe recv redo ref rename require reset return reverse rewinddir rindex
        rmdir s say scalar seek seekdir select semctl semget semop send setgrent sethostent
        setnetent setpgrp setpriority setprotoent setpwent setservent setsockopt shift shmctl
        shmget shmread shmwrite shutdown sin sleep socket socketpair sort splice split sprintf
        sqrt srand stat state study sub substr symlink syscall sysopen sysread sysseek system
        syswrite tell telldir tie tied time times tr truncate uc ucfirst umask undef unless
        unlink unpack unshift untie until use utime values vec wait waitpid wantarray warn when
        while write x xor y
        """),
    ),
    stc.STC_LEX_PHPSCRIPT: (
        ('PHP Keywords', 0, ''),
    ),
    stc.STC_LEX_POWERSHELL: (
        ('Commands', 0, ''),
        ('Cmdlets', 1,
        """
        Add-AppxPackage Add-AppxProvisionedPackage Add-AppxVolume Add-BitsFile
        Add-CertificateEnrollmentPolicyServer Add-Content Add-History Add-KdsRootKey Add-LocalGroupMember
        Add-Member Add-Type Add-WindowsCapability Add-WindowsDriver Add-WindowsImage Add-WindowsPackage
        Clear-Content Clear-History Clear-Item Clear-ItemProperty Clear-KdsCache Clear-Tpm Clear-Variable
        Clear-WindowsCorruptMountPoint Compare-Object Complete-BitsTransfer Confirm-SecureBootUEFI
        Connect-PSSession Connect-WSMan Convert-Path ConvertFrom-Csv ConvertFrom-Json ConvertFrom-Markdown
        ConvertFrom-SddlString ConvertFrom-SecureString ConvertFrom-StringData ConvertTo-Csv
        ConvertTo-Html ConvertTo-Json ConvertTo-ProcessMitigationPolicy ConvertTo-SecureString
        ConvertTo-TpmOwnerAuth ConvertTo-Xml Copy-Item Copy-ItemProperty Debug-Job Debug-Process
        Debug-Runspace Delete-DeliveryOptimizationCache Disable-AppBackgroundTaskDiagnosticLog
        Disable-ExperimentalFeature Disable-LocalUser Disable-PSBreakpoint Disable-PSRemoting
        Disable-PSSessionConfiguration Disable-RunspaceDebug Disable-TlsCipherSuite Disable-TlsEccCurve
        Disable-TlsSessionTicketKey Disable-TpmAutoProvisioning Disable-WindowsErrorReporting
        Disable-WindowsOptionalFeature Disable-WSManCredSSP Disconnect-PSSession Disconnect-WSMan
        Dismount-AppxVolume Dismount-WindowsImage Enable-AppBackgroundTaskDiagnosticLog
        Enable-ExperimentalFeature Enable-LocalUser Enable-PSBreakpoint Enable-PSRemoting
        Enable-PSSessionConfiguration Enable-RunspaceDebug Enable-TlsCipherSuite Enable-TlsEccCurve
        Enable-TlsSessionTicketKey Enable-TpmAutoProvisioning Enable-WindowsErrorReporting
        Enable-WindowsOptionalFeature Enable-WSManCredSSP Enter-PSHostProcess Enter-PSSession
        Exit-PSHostProcess Exit-PSSession Expand-WindowsCustomDataImage Expand-WindowsImage Export-Alias
        Export-BinaryMiLog Export-Certificate Export-Clixml Export-Counter Export-Csv Export-FormatData
        Export-ModuleMember Export-PfxCertificate Export-ProvisioningPackage Export-PSSession
        Export-StartLayout Export-StartLayoutEdgeAssets Export-TlsSessionTicketKey Export-Trace
        Export-WindowsCapabilitySource Export-WindowsDriver Export-WindowsImage Find-Package
        Find-PackageProvider ForEach-Object Format-Custom Format-Hex Format-List Format-SecureBootUEFI
        Format-Table Format-Wide Get-Acl Get-Alias Get-AppxDefaultVolume Get-AppxPackage
        Get-AppxPackageManifest Get-AppxProvisionedPackage Get-AppxVolume Get-AuthenticodeSignature
        Get-BitsTransfer Get-Certificate Get-CertificateAutoEnrollmentPolicy
        Get-CertificateEnrollmentPolicyServer Get-CertificateNotificationTask Get-ChildItem
        Get-CimAssociatedInstance Get-CimClass Get-CimInstance Get-CimSession Get-CmsMessage Get-Command
        Get-ComputerInfo Get-Content Get-Counter Get-Credential Get-Culture Get-DAPolicyChange Get-Date
        Get-DeliveryOptimizationLog Get-DeliveryOptimizationLogAnalysis Get-Event Get-EventSubscriber
        Get-ExecutionPolicy Get-ExperimentalFeature Get-FileHash Get-FormatData Get-Help Get-History
        Get-Host Get-InstalledLanguage Get-Item Get-ItemProperty Get-ItemPropertyValue Get-Job
        Get-KdsConfiguration Get-KdsRootKey Get-LocalGroup Get-LocalGroupMember Get-LocalUser Get-Location
        Get-MarkdownOption Get-Member Get-Module Get-NonRemovableAppsPolicy Get-Package
        Get-PackageProvider Get-PackageSource Get-PfxCertificate Get-PfxData Get-Process
        Get-ProcessMitigation Get-ProvisioningPackage Get-PSBreakpoint Get-PSCallStack Get-PSDrive
        Get-PSHostProcessInfo Get-PSProvider Get-PSReadLineKeyHandler Get-PSReadLineOption Get-PSSession
        Get-PSSessionCapability Get-PSSessionConfiguration Get-Random Get-Runspace Get-RunspaceDebug
        Get-SecureBootPolicy Get-SecureBootUEFI Get-Service Get-SystemPreferredUILanguage Get-TimeZone
        Get-TlsCipherSuite Get-TlsEccCurve Get-Tpm Get-TpmEndorsementKeyInfo Get-TpmSupportedFeature
        Get-TraceSource Get-TroubleshootingPack Get-TrustedProvisioningCertificate Get-TypeData
        Get-UICulture Get-Unique Get-Uptime Get-Variable Get-Verb Get-WheaMemoryPolicy Get-WIMBootEntry
        Get-WinAcceptLanguageFromLanguageListOptOut Get-WinCultureFromLanguageListOptOut
        Get-WinDefaultInputMethodOverride Get-WindowsCapability Get-WindowsDeveloperLicense
        Get-WindowsDriver Get-WindowsEdition Get-WindowsErrorReporting Get-WindowsImage
        Get-WindowsImageContent Get-WindowsOptionalFeature Get-WindowsPackage
        Get-WindowsReservedStorageState Get-WindowsSearchSetting Get-WinEvent Get-WinHomeLocation
        Get-WinLanguageBarOption Get-WinSystemLocale Get-WinUILanguageOverride Get-WinUserLanguageList
        Get-WSManCredSSP Get-WSManInstance Group-Object Import-Alias Import-BinaryMiLog Import-Certificate
        Import-Clixml Import-Counter Import-Csv Import-LocalizedData Import-Module Import-PackageProvider
        Import-PfxCertificate Import-PowerShellDataFile Import-PSSession Import-StartLayout
        Import-TpmOwnerAuth Initialize-Tpm Install-Language Install-Package Install-PackageProvider
        Install-ProvisioningPackage Install-TrustedProvisioningCertificate Invoke-CimMethod Invoke-Command
        Invoke-CommandInDesktopPackage Invoke-Expression Invoke-History Invoke-Item Invoke-RestMethod
        Invoke-TroubleshootingPack Invoke-WebRequest Invoke-WSManAction Join-Path Join-String
        Measure-Command Measure-Object Mount-AppxVolume Mount-WindowsImage Move-AppxPackage Move-Item
        Move-ItemProperty New-Alias New-CertificateNotificationTask New-CimInstance New-CimSession
        New-CimSessionOption New-Event New-FileCatalog New-Guid New-Item New-ItemProperty New-LocalGroup
        New-LocalUser New-Module New-ModuleManifest New-NetIPsecAuthProposal
        New-NetIPsecMainModeCryptoProposal New-NetIPsecQuickModeCryptoProposal New-Object
        New-ProvisioningRepro New-PSDrive New-PSRoleCapabilityFile New-PSSession
        New-PSSessionConfigurationFile New-PSSessionOption New-PSTransportOption New-SelfSignedCertificate
        New-Service New-TemporaryFile New-TimeSpan New-TlsSessionTicketKey New-Variable
        New-WindowsCustomImage New-WindowsImage New-WinEvent New-WinUserLanguageList New-WSManInstance
        New-WSManSessionOption Optimize-AppxProvisionedPackages Optimize-WindowsImage Out-Default Out-File
        Out-Host Out-Null Out-String Pop-Location Protect-CmsMessage Push-Location Read-Host Receive-Job
        Receive-PSSession Register-ArgumentCompleter Register-CimIndicationEvent Register-EngineEvent
        Register-ObjectEvent Register-PackageSource Register-PSSessionConfiguration Remove-Alias
        Remove-AppxPackage Remove-AppxProvisionedPackage Remove-AppxVolume Remove-BitsTransfer
        Remove-CertificateEnrollmentPolicyServer Remove-CertificateNotificationTask Remove-CimInstance
        Remove-CimSession Remove-Event Remove-Item Remove-ItemProperty Remove-Job Remove-LocalGroup
        Remove-LocalGroupMember Remove-LocalUser Remove-Module Remove-PSBreakpoint Remove-PSDrive
        Remove-PSReadLineKeyHandler Remove-PSSession Remove-Service Remove-TypeData Remove-Variable
        Remove-WindowsCapability Remove-WindowsDriver Remove-WindowsImage Remove-WindowsPackage
        Remove-WSManInstance Rename-Computer Rename-Item Rename-ItemProperty Rename-LocalGroup
        Rename-LocalUser Repair-WindowsImage Resolve-DnsName Resolve-Path Restart-Computer Restart-Service
        Resume-BitsTransfer Resume-ProvisioningSession Resume-Service Save-Help Save-Package
        Save-WindowsImage Select-Object Select-String Select-Xml Send-MailMessage Set-Acl Set-Alias
        Set-AppBackgroundTaskResourcePolicy Set-AppxDefaultVolume Set-AppXProvisionedDataFile
        Set-AuthenticodeSignature Set-BitsTransfer Set-CertificateAutoEnrollmentPolicy Set-CimInstance
        Set-Content Set-Culture Set-Date Set-DeliveryOptimizationStatus Set-DODownloadMode
        Set-DOPercentageMaxBackgroundBandwidth Set-DOPercentageMaxForegroundBandwidth Set-ExecutionPolicy
        Set-Item Set-ItemProperty Set-KdsConfiguration Set-LocalGroup Set-LocalUser Set-Location
        Set-MarkdownOption Set-NonRemovableAppsPolicy Set-PackageSource Set-ProcessMitigation
        Set-PSBreakpoint Set-PSDebug Set-PSReadLineKeyHandler Set-PSReadLineOption
        Set-PSSessionConfiguration Set-SecureBootUEFI Set-Service Set-StrictMode
        Set-SystemPreferredUILanguage Set-TimeZone Set-TpmOwnerAuth Set-TraceSource Set-Variable
        Set-WheaMemoryPolicy Set-WinAcceptLanguageFromLanguageListOptOut
        Set-WinCultureFromLanguageListOptOut Set-WinDefaultInputMethodOverride Set-WindowsEdition
        Set-WindowsProductKey Set-WindowsReservedStorageState Set-WindowsSearchSetting Set-WinHomeLocation
        Set-WinLanguageBarOption Set-WinSystemLocale Set-WinUILanguageOverride Set-WinUserLanguageList
        Set-WSManInstance Set-WSManQuickConfig Show-Markdown Show-WindowsDeveloperLicenseRegistration
        Sort-Object Split-Path Split-WindowsImage Start-BitsTransfer Start-Job Start-OSUninstall
        Start-Process Start-Service Start-Sleep Start-ThreadJob Start-Transcript Stop-Computer Stop-Job
        Stop-Process Stop-Service Stop-Transcript Suspend-BitsTransfer Suspend-Service Switch-Certificate
        Tee-Object Test-Certificate Test-Connection Test-FileCatalog Test-Json Test-KdsRootKey
        Test-ModuleManifest Test-Path Test-PSSessionConfigurationFile Test-WSMan Trace-Command
        Unblock-File Unblock-Tpm Uninstall-Language Uninstall-Package Uninstall-ProvisioningPackage
        Uninstall-TrustedProvisioningCertificate Unprotect-CmsMessage Unregister-Event
        Unregister-PackageSource Unregister-PSSessionConfiguration Unregister-WindowsDeveloperLicense
        Update-FormatData Update-Help Update-TypeData Update-WIMBootEntry Use-WindowsUnattend
        Wait-Debugger Wait-Event Wait-Job Wait-Process Where-Object Write-Debug Write-Error Write-Host
        Write-Information Write-Output Write-Progress Write-Verbose Write-Warning
        """),
        ('Aliases', 2,
        """
        % ? ac Add-AppPackage Add-AppPackageVolume Add-AppProvisionedPackage Add-ProvisionedAppPackage
        Add-ProvisionedAppxPackage Add-ProvisioningPackage Add-TrustedProvisioningCertificate algm
        Apply-WindowsUnattend blsmba cat cd chdir clc clear clhy cli clp cls clv cnsn compare copy cp cpi
        cpp cssmbo cssmbse cvpa dbp del diff dir Disable-PhysicalDiskIndication
        Disable-StorageDiagnosticLog Dismount-AppPackageVolume dlu dnsn dsmbd ebp echo elu
        Enable-PhysicalDiskIndication Enable-StorageDiagnosticLog epal epcsv erase esmbd etsn exsn fc fhx
        fimo fl Flush-Volume foreach ft fw gal gbp gc gcai gci gcim gcls gcm gcms gcs gdr Get-AppPackage
        Get-AppPackageDefaultVolume Get-AppPackageLastError Get-AppPackageLog Get-AppPackageManifest
        Get-AppPackageVolume Get-AppProvisionedPackage Get-DiskSNV Get-Language Get-PhysicalDiskSNV
        Get-PreferredLanguage Get-ProvisionedAppPackage Get-ProvisionedAppxPackage Get-StorageEnclosureSNV
        Get-SystemLanguage ghy gi gin gip gjb gl glg glgm glu gm gmo gp gps gpv group grsmba gsmba gsmbb
        gsmbc gsmbcc gsmbcn gsmbd gsmbgm gsmbm gsmbmc gsmbo gsmbs gsmbsc gsmbscm gsmbse gsmbsn gsmbt gsmbw
        gsn gsv gtz gu gv h history icim icm iex ihy ii Initialize-Volume inmo ipal ipcsv ipmo irm iru iwr
        kill ls man md measure mi mount Mount-AppPackageVolume move Move-AppPackage Move-SmbClient mp
        msmbw mv nal ncim ncms ncso ndr ni nlg nlu nmo nsmbgm nsmbm nsmbs nsmbscm nsmbt nsn nv oh
        Optimize-AppProvisionedPackages Optimize-ProvisionedAppPackages Optimize-ProvisionedAppxPackages
        pfn popd ps pumo pushd pwd r rbp rcie rcim rcjb rcms rcsn rd rdr Remove-AppPackage
        Remove-AppPackageVolume Remove-AppProvisionedPackage Remove-EtwTraceSession
        Remove-ProvisionedAppPackage Remove-ProvisionedAppxPackage Remove-ProvisioningPackage
        Remove-TrustedProvisioningCertificate ren ri rjb rksmba rlg rlgm rlu rm rmdir rmo rni rnlg rnlu
        rnp rp rsmbb rsmbc rsmbgm rsmbm rsmbs rsmbscm rsmbt rsn rv rvpa sajb sal saps sasv sbp scim select
        set Set-AppPackageDefaultVolume Set-AppPackageProvisionedDataFile Set-AutologgerConfig
        Set-EtwTraceSession Set-PreferredLanguage Set-ProvisionedAppPackageDataFile
        Set-ProvisionedAppXDataFile Set-SystemLanguage si sl sleep slg sls slu sort sp spjb spps spsv
        ssmbb ssmbcc ssmbp ssmbs ssmbsc start stz sv tee tid TNC type udsmbmc ulsmba upmo where wjb write
        Write-FileSystemCache
        """),
        ('Functions', 3,
        """
        Add-BCDataCacheExtension Add-BitLockerKeyProtector Add-DnsClientNrptRule Add-EtwTraceProvider
        Add-InitiatorIdToMaskingSet Add-MpPreference Add-NetEventNetworkAdapter
        Add-NetEventPacketCaptureProvider Add-NetEventProvider Add-NetEventVFPProvider
        Add-NetEventVmNetworkAdapter Add-NetEventVmSwitch Add-NetEventVmSwitchProvider
        Add-NetEventWFPCaptureProvider Add-NetIPHttpsCertBinding Add-NetLbfoTeamMember Add-NetLbfoTeamNic
        Add-NetNatExternalAddress Add-NetNatStaticMapping Add-NetSwitchTeamMember Add-NodeKeys Add-OdbcDsn
        Add-PartitionAccessPath Add-PhysicalDisk Add-Printer Add-PrinterDriver Add-PrinterPort
        Add-StorageFaultDomain Add-TargetPortToMaskingSet Add-VirtualDiskToMaskingSet Add-VpnConnection
        Add-VpnConnectionRoute Add-VpnConnectionTriggerApplication
        Add-VpnConnectionTriggerDnsConfiguration Add-VpnConnectionTriggerTrustedNetwork
        AddDscResourceProperty AddDscResourcePropertyFromMetadata Backup-BitLockerKeyProtector
        BackupToAAD-BitLockerKeyProtector Block-FileShareAccess Block-SmbShareAccess cd.. cd\
        CheckResourceFound Clear-AssignedAccess Clear-BCCache Clear-BitLockerAutoUnlock Clear-Disk
        Clear-DnsClientCache Clear-FileStorageTier Clear-Host Clear-PcsvDeviceLog
        Clear-StorageDiagnosticInfo Close-SmbOpenFile Close-SmbSession Compress-Archive Configuration
        Connect-VirtualDisk ConvertTo-MOFInstance Copy-NetFirewallRule Copy-NetIPsecMainModeCryptoSet
        Copy-NetIPsecMainModeRule Copy-NetIPsecPhase1AuthSet Copy-NetIPsecPhase2AuthSet
        Copy-NetIPsecQuickModeCryptoSet Copy-NetIPsecRule Debug-FileShare Debug-MMAppPrelaunch
        Debug-StorageSubSystem Debug-Volume Disable-BC Disable-BCDowngrading Disable-BCServeOnBattery
        Disable-BitLocker Disable-BitLockerAutoUnlock Disable-DAManualEntryPointSelection
        Disable-DeliveryOptimizationVerboseLogs Disable-MMAgent Disable-NetAdapter
        Disable-NetAdapterBinding Disable-NetAdapterChecksumOffload
        Disable-NetAdapterEncapsulatedPacketTaskOffload Disable-NetAdapterIPsecOffload
        Disable-NetAdapterLso Disable-NetAdapterPacketDirect Disable-NetAdapterPowerManagement
        Disable-NetAdapterQos Disable-NetAdapterRdma Disable-NetAdapterRsc Disable-NetAdapterRss
        Disable-NetAdapterSriov Disable-NetAdapterUso Disable-NetAdapterVmq
        Disable-NetDnsTransitionConfiguration Disable-NetFirewallRule Disable-NetIPHttpsProfile
        Disable-NetIPsecMainModeRule Disable-NetIPsecRule Disable-NetNatTransitionConfiguration
        Disable-NetworkSwitchEthernetPort Disable-NetworkSwitchFeature Disable-NetworkSwitchVlan
        Disable-OdbcPerfCounter Disable-PhysicalDiskIdentification Disable-PnpDevice Disable-PSTrace
        Disable-PSWSManCombinedTrace Disable-ScheduledTask Disable-SmbDelegation
        Disable-StorageEnclosureIdentification Disable-StorageEnclosurePower
        Disable-StorageHighAvailability Disable-StorageMaintenanceMode Disable-WdacBidTrace
        Disable-WSManTrace Disconnect-VirtualDisk Dismount-DiskImage Enable-BCDistributed
        Enable-BCDowngrading Enable-BCHostedClient Enable-BCHostedServer Enable-BCLocal
        Enable-BCServeOnBattery Enable-BitLocker Enable-BitLockerAutoUnlock
        Enable-DAManualEntryPointSelection Enable-DeliveryOptimizationVerboseLogs Enable-MMAgent
        Enable-NetAdapter Enable-NetAdapterBinding Enable-NetAdapterChecksumOffload
        Enable-NetAdapterEncapsulatedPacketTaskOffload Enable-NetAdapterIPsecOffload Enable-NetAdapterLso
        Enable-NetAdapterPacketDirect Enable-NetAdapterPowerManagement Enable-NetAdapterQos
        Enable-NetAdapterRdma Enable-NetAdapterRsc Enable-NetAdapterRss Enable-NetAdapterSriov
        Enable-NetAdapterUso Enable-NetAdapterVmq Enable-NetDnsTransitionConfiguration
        Enable-NetFirewallRule Enable-NetIPHttpsProfile Enable-NetIPsecMainModeRule Enable-NetIPsecRule
        Enable-NetNatTransitionConfiguration Enable-NetworkSwitchEthernetPort Enable-NetworkSwitchFeature
        Enable-NetworkSwitchVlan Enable-OdbcPerfCounter Enable-PhysicalDiskIdentification Enable-PnpDevice
        Enable-PSTrace Enable-PSWSManCombinedTrace Enable-ScheduledTask Enable-SmbDelegation
        Enable-StorageEnclosureIdentification Enable-StorageEnclosurePower Enable-StorageHighAvailability
        Enable-StorageMaintenanceMode Enable-WdacBidTrace Enable-WSManTrace Expand-Archive
        Export-BCCachePackage Export-BCSecretKey Export-ScheduledTask Find-Command Find-DSCResource
        Find-Module Find-NetIPsecRule Find-NetRoute Find-RoleCapability Find-Script Flush-EtwTraceSession
        Format-Volume Generate-VersionInfo Get-AppBackgroundTask Get-AppxLastError Get-AppxLog
        Get-AssignedAccess Get-AutologgerConfig Get-BCClientConfiguration Get-BCContentServerConfiguration
        Get-BCDataCache Get-BCDataCacheExtension Get-BCHashCache Get-BCHostedCacheServerConfiguration
        Get-BCNetworkConfiguration Get-BCStatus Get-BitLockerVolume Get-ClusteredScheduledTask
        Get-CompatibleVersionAddtionaPropertiesStr Get-ComplexResourceQualifier
        Get-ConfigurationErrorCount Get-DAClientExperienceConfiguration Get-DAConnectionStatus
        Get-DAEntryPointTableItem Get-DedupProperties Get-DeliveryOptimizationPerfSnap
        Get-DeliveryOptimizationPerfSnapThisMonth Get-DeliveryOptimizationStatus Get-Disk Get-DiskImage
        Get-DiskStorageNodeView Get-DnsClient Get-DnsClientCache Get-DnsClientGlobalSetting
        Get-DnsClientNrptGlobal Get-DnsClientNrptPolicy Get-DnsClientNrptRule Get-DnsClientServerAddress
        Get-DOConfig Get-DODownloadMode Get-DOPercentageMaxBackgroundBandwidth
        Get-DOPercentageMaxForegroundBandwidth Get-DscResource Get-DSCResourceModules
        Get-EncryptedPassword Get-EtwTraceProvider Get-EtwTraceSession Get-FileIntegrity Get-FileShare
        Get-FileShareAccessControlEntry Get-FileStorageTier Get-InitiatorId Get-InitiatorPort
        Get-InnerMostErrorRecord Get-InstalledModule Get-InstalledScript Get-LogProperties Get-MaskingSet
        Get-MMAgent Get-MofInstanceName Get-MofInstanceText Get-MpComputerStatus Get-MpPerformanceReport
        Get-MpPreference Get-MpThreat Get-MpThreatCatalog Get-MpThreatDetection
        Get-NCSIPolicyConfiguration Get-Net6to4Configuration Get-NetAdapter Get-NetAdapterAdvancedProperty
        Get-NetAdapterBinding Get-NetAdapterChecksumOffload Get-NetAdapterEncapsulatedPacketTaskOffload
        Get-NetAdapterHardwareInfo Get-NetAdapterIPsecOffload Get-NetAdapterLso Get-NetAdapterPacketDirect
        Get-NetAdapterPowerManagement Get-NetAdapterQos Get-NetAdapterRdma Get-NetAdapterRsc
        Get-NetAdapterRss Get-NetAdapterSriov Get-NetAdapterSriovVf Get-NetAdapterStatistics
        Get-NetAdapterUso Get-NetAdapterVmq Get-NetAdapterVMQQueue Get-NetAdapterVPort Get-NetCompartment
        Get-NetConnectionProfile Get-NetDnsTransitionConfiguration Get-NetDnsTransitionMonitoring
        Get-NetEventNetworkAdapter Get-NetEventPacketCaptureProvider Get-NetEventProvider
        Get-NetEventSession Get-NetEventVFPProvider Get-NetEventVmNetworkAdapter Get-NetEventVmSwitch
        Get-NetEventVmSwitchProvider Get-NetEventWFPCaptureProvider Get-NetFirewallAddressFilter
        Get-NetFirewallApplicationFilter Get-NetFirewallDynamicKeywordAddress
        Get-NetFirewallInterfaceFilter Get-NetFirewallInterfaceTypeFilter Get-NetFirewallPortFilter
        Get-NetFirewallProfile Get-NetFirewallRule Get-NetFirewallSecurityFilter
        Get-NetFirewallServiceFilter Get-NetFirewallSetting Get-NetIPAddress Get-NetIPConfiguration
        Get-NetIPHttpsConfiguration Get-NetIPHttpsState Get-NetIPInterface Get-NetIPsecDospSetting
        Get-NetIPsecMainModeCryptoSet Get-NetIPsecMainModeRule Get-NetIPsecMainModeSA
        Get-NetIPsecPhase1AuthSet Get-NetIPsecPhase2AuthSet Get-NetIPsecQuickModeCryptoSet
        Get-NetIPsecQuickModeSA Get-NetIPsecRule Get-NetIPv4Protocol Get-NetIPv6Protocol
        Get-NetIsatapConfiguration Get-NetLbfoTeam Get-NetLbfoTeamMember Get-NetLbfoTeamNic Get-NetNat
        Get-NetNatExternalAddress Get-NetNatGlobal Get-NetNatSession Get-NetNatStaticMapping
        Get-NetNatTransitionConfiguration Get-NetNatTransitionMonitoring Get-NetNeighbor
        Get-NetOffloadGlobalSetting Get-NetPrefixPolicy Get-NetQosPolicy Get-NetRoute Get-NetSwitchTeam
        Get-NetSwitchTeamMember Get-NetTCPConnection Get-NetTCPSetting Get-NetTeredoConfiguration
        Get-NetTeredoState Get-NetTransportFilter Get-NetUDPEndpoint Get-NetUDPSetting
        Get-NetworkSwitchEthernetPort Get-NetworkSwitchFeature Get-NetworkSwitchGlobalData
        Get-NetworkSwitchVlan Get-OdbcDriver Get-OdbcDsn Get-OdbcPerfCounter
        Get-OffloadDataTransferSetting Get-Partition Get-PartitionSupportedSize Get-PcsvDevice
        Get-PcsvDeviceLog Get-PhysicalDisk Get-PhysicalDiskStorageNodeView Get-PhysicalExtent
        Get-PhysicalExtentAssociation Get-PnpDevice Get-PnpDeviceProperty Get-PositionInfo
        Get-PrintConfiguration Get-Printer Get-PrinterDriver Get-PrinterPort Get-PrinterProperty
        Get-PrintJob Get-PSCurrentConfigurationNode Get-PSDefaultConfigurationDocument
        Get-PSMetaConfigDocumentInstVersionInfo Get-PSMetaConfigurationProcessed Get-PSRepository
        Get-PSTopConfigurationName Get-PublicKeyFromFile Get-PublicKeyFromStore Get-ResiliencySetting
        Get-ScheduledTask Get-ScheduledTaskInfo Get-SmbBandWidthLimit Get-SmbClientConfiguration
        Get-SmbClientNetworkInterface Get-SmbConnection Get-SmbDelegation Get-SmbGlobalMapping
        Get-SmbMapping Get-SmbMultichannelConnection Get-SmbMultichannelConstraint Get-SmbOpenFile
        Get-SmbServerCertificateMapping Get-SmbServerConfiguration Get-SmbServerNetworkInterface
        Get-SmbSession Get-SmbShare Get-SmbShareAccess Get-SmbWitnessClient Get-StartApps
        Get-StorageAdvancedProperty Get-StorageChassis Get-StorageDiagnosticInfo Get-StorageEnclosure
        Get-StorageEnclosureStorageNodeView Get-StorageEnclosureVendorData Get-StorageExtendedStatus
        Get-StorageFaultDomain Get-StorageFileServer Get-StorageFirmwareInformation
        Get-StorageHealthAction Get-StorageHealthReport Get-StorageHealthSetting Get-StorageHistory
        Get-StorageJob Get-StorageNode Get-StoragePool Get-StorageProvider Get-StorageRack
        Get-StorageReliabilityCounter Get-StorageScaleUnit Get-StorageSetting Get-StorageSite
        Get-StorageSubSystem Get-StorageTier Get-StorageTierSupportedSize Get-SupportedClusterSizes
        Get-SupportedFileSystems Get-TargetPort Get-TargetPortal Get-VirtualDisk
        Get-VirtualDiskSupportedSize Get-Volume Get-VolumeCorruptionCount Get-VolumeScrubPolicy
        Get-VpnConnection Get-VpnConnectionTrigger Get-WdacBidTrace Get-WindowsUpdateLog Get-WUAVersion
        Get-WUIsPendingReboot Get-WULastInstallationDate Get-WULastScanSuccessDate GetCompositeResource
        GetImplementingModulePath GetModule GetPatterns GetResourceFromKeyword GetSyntax
        Grant-FileShareAccess Grant-SmbShareAccess help Hide-VirtualDisk Import-BCCachePackage
        Import-BCSecretKey ImportCimAndScriptKeywordsFromModule ImportClassResourcesFromModule
        Initialize-ConfigurationRuntimeState Initialize-Disk Install-Module Install-Script
        Install-WUUpdates IsHiddenResource IsPatternMatched Lock-BitLocker mkdir Mount-DiskImage
        Move-SmbWitnessClient New-AutologgerConfig New-DAEntryPointTableItem New-DscChecksum
        New-EapConfiguration New-EtwTraceSession New-FileShare New-MaskingSet New-MpPerformanceRecording
        New-NetAdapterAdvancedProperty New-NetEventSession New-NetFirewallDynamicKeywordAddress
        New-NetFirewallRule New-NetIPAddress New-NetIPHttpsConfiguration New-NetIPsecDospSetting
        New-NetIPsecMainModeCryptoSet New-NetIPsecMainModeRule New-NetIPsecPhase1AuthSet
        New-NetIPsecPhase2AuthSet New-NetIPsecQuickModeCryptoSet New-NetIPsecRule New-NetLbfoTeam
        New-NetNat New-NetNatTransitionConfiguration New-NetNeighbor New-NetQosPolicy New-NetRoute
        New-NetSwitchTeam New-NetTransportFilter New-NetworkSwitchVlan New-Partition New-ScheduledTask
        New-ScheduledTaskAction New-ScheduledTaskPrincipal New-ScheduledTaskSettingsSet
        New-ScheduledTaskTrigger New-ScriptFileInfo New-SmbGlobalMapping New-SmbMapping
        New-SmbMultichannelConstraint New-SmbServerCertificateMapping New-SmbShare New-StorageFileServer
        New-StoragePool New-StorageSubsystemVirtualDisk New-StorageTier New-VirtualDisk
        New-VirtualDiskClone New-VirtualDiskSnapshot New-Volume New-VpnServerAddress Node Open-NetGPO
        Optimize-StoragePool Optimize-Volume oss Pause prompt PSConsoleHostReadLine Publish-BCFileContent
        Publish-BCWebContent Publish-Module Publish-Script Read-PrinterNfcTag ReadEnvironmentFile
        Register-ClusteredScheduledTask Register-DnsClient Register-PSRepository Register-ScheduledTask
        Register-StorageSubsystem Remove-AutologgerConfig Remove-BCDataCacheExtension
        Remove-BitLockerKeyProtector Remove-DAEntryPointTableItem Remove-DnsClientNrptRule
        Remove-EtwTraceProvider Remove-FileShare Remove-InitiatorId Remove-InitiatorIdFromMaskingSet
        Remove-MaskingSet Remove-MpPreference Remove-MpThreat Remove-NetAdapterAdvancedProperty
        Remove-NetEventNetworkAdapter Remove-NetEventPacketCaptureProvider Remove-NetEventProvider
        Remove-NetEventSession Remove-NetEventVFPProvider Remove-NetEventVmNetworkAdapter
        Remove-NetEventVmSwitch Remove-NetEventVmSwitchProvider Remove-NetEventWFPCaptureProvider
        Remove-NetFirewallDynamicKeywordAddress Remove-NetFirewallRule Remove-NetIPAddress
        Remove-NetIPHttpsCertBinding Remove-NetIPHttpsConfiguration Remove-NetIPsecDospSetting
        Remove-NetIPsecMainModeCryptoSet Remove-NetIPsecMainModeRule Remove-NetIPsecMainModeSA
        Remove-NetIPsecPhase1AuthSet Remove-NetIPsecPhase2AuthSet Remove-NetIPsecQuickModeCryptoSet
        Remove-NetIPsecQuickModeSA Remove-NetIPsecRule Remove-NetLbfoTeam Remove-NetLbfoTeamMember
        Remove-NetLbfoTeamNic Remove-NetNat Remove-NetNatExternalAddress Remove-NetNatStaticMapping
        Remove-NetNatTransitionConfiguration Remove-NetNeighbor Remove-NetQosPolicy Remove-NetRoute
        Remove-NetSwitchTeam Remove-NetSwitchTeamMember Remove-NetTransportFilter
        Remove-NetworkSwitchEthernetPortIPAddress Remove-NetworkSwitchVlan Remove-OdbcDsn Remove-Partition
        Remove-PartitionAccessPath Remove-PhysicalDisk Remove-Printer Remove-PrinterDriver
        Remove-PrinterPort Remove-PrintJob Remove-SmbBandwidthLimit Remove-SMBComponent
        Remove-SmbGlobalMapping Remove-SmbMapping Remove-SmbMultichannelConstraint
        Remove-SmbServerCertificateMapping Remove-SmbShare Remove-StorageFaultDomain
        Remove-StorageFileServer Remove-StorageHealthIntent Remove-StorageHealthSetting Remove-StoragePool
        Remove-StorageTier Remove-TargetPortFromMaskingSet Remove-VirtualDisk
        Remove-VirtualDiskFromMaskingSet Remove-VpnConnection Remove-VpnConnectionRoute
        Remove-VpnConnectionTriggerApplication Remove-VpnConnectionTriggerDnsConfiguration
        Remove-VpnConnectionTriggerTrustedNetwork Rename-DAEntryPointTableItem Rename-MaskingSet
        Rename-NetAdapter Rename-NetFirewallRule Rename-NetIPHttpsConfiguration
        Rename-NetIPsecMainModeCryptoSet Rename-NetIPsecMainModeRule Rename-NetIPsecPhase1AuthSet
        Rename-NetIPsecPhase2AuthSet Rename-NetIPsecQuickModeCryptoSet Rename-NetIPsecRule
        Rename-NetLbfoTeam Rename-NetSwitchTeam Rename-Printer Repair-FileIntegrity Repair-VirtualDisk
        Repair-Volume Reset-BC Reset-DAClientExperienceConfiguration Reset-DAEntryPointTableItem
        Reset-NCSIPolicyConfiguration Reset-Net6to4Configuration Reset-NetAdapterAdvancedProperty
        Reset-NetDnsTransitionConfiguration Reset-NetIPHttpsConfiguration Reset-NetIsatapConfiguration
        Reset-NetTeredoConfiguration Reset-PhysicalDisk Reset-StorageReliabilityCounter Resize-Partition
        Resize-StorageTier Resize-VirtualDisk Restart-NetAdapter Restart-PcsvDevice Restart-PrintJob
        Restore-NetworkSwitchConfiguration Resume-BitLocker Resume-PrintJob Revoke-FileShareAccess
        Revoke-SmbShareAccess Save-EtwTraceSession Save-Module Save-NetGPO Save-NetworkSwitchConfiguration
        Save-Script Send-EtwTraceSession Set-AssignedAccess Set-BCAuthentication Set-BCCache
        Set-BCDataCacheEntryMaxAge Set-BCMinSMBLatency Set-BCSecretKey Set-ClusteredScheduledTask
        Set-DAClientExperienceConfiguration Set-DAEntryPointTableItem Set-Disk Set-DnsClient
        Set-DnsClientGlobalSetting Set-DnsClientNrptGlobal Set-DnsClientNrptRule
        Set-DnsClientServerAddress Set-EtwTraceProvider Set-FileIntegrity Set-FileShare
        Set-FileStorageTier Set-InitiatorPort Set-LogProperties Set-MMAgent Set-MpPreference
        Set-NCSIPolicyConfiguration Set-Net6to4Configuration Set-NetAdapter Set-NetAdapterAdvancedProperty
        Set-NetAdapterBinding Set-NetAdapterChecksumOffload Set-NetAdapterEncapsulatedPacketTaskOffload
        Set-NetAdapterIPsecOffload Set-NetAdapterLso Set-NetAdapterPacketDirect
        Set-NetAdapterPowerManagement Set-NetAdapterQos Set-NetAdapterRdma Set-NetAdapterRsc
        Set-NetAdapterRss Set-NetAdapterSriov Set-NetAdapterUso Set-NetAdapterVmq Set-NetConnectionProfile
        Set-NetDnsTransitionConfiguration Set-NetEventPacketCaptureProvider Set-NetEventProvider
        Set-NetEventSession Set-NetEventVFPProvider Set-NetEventVmSwitchProvider
        Set-NetEventWFPCaptureProvider Set-NetFirewallAddressFilter Set-NetFirewallApplicationFilter
        Set-NetFirewallInterfaceFilter Set-NetFirewallInterfaceTypeFilter Set-NetFirewallPortFilter
        Set-NetFirewallProfile Set-NetFirewallRule Set-NetFirewallSecurityFilter
        Set-NetFirewallServiceFilter Set-NetFirewallSetting Set-NetIPAddress Set-NetIPHttpsConfiguration
        Set-NetIPInterface Set-NetIPsecDospSetting Set-NetIPsecMainModeCryptoSet Set-NetIPsecMainModeRule
        Set-NetIPsecPhase1AuthSet Set-NetIPsecPhase2AuthSet Set-NetIPsecQuickModeCryptoSet
        Set-NetIPsecRule Set-NetIPv4Protocol Set-NetIPv6Protocol Set-NetIsatapConfiguration
        Set-NetLbfoTeam Set-NetLbfoTeamMember Set-NetLbfoTeamNic Set-NetNat Set-NetNatGlobal
        Set-NetNatTransitionConfiguration Set-NetNeighbor Set-NetOffloadGlobalSetting Set-NetQosPolicy
        Set-NetRoute Set-NetTCPSetting Set-NetTeredoConfiguration Set-NetUDPSetting
        Set-NetworkSwitchEthernetPortIPAddress Set-NetworkSwitchPortMode Set-NetworkSwitchPortProperty
        Set-NetworkSwitchVlanProperty Set-NodeExclusiveResources Set-NodeManager Set-NodeResources
        Set-NodeResourceSource Set-OdbcDriver Set-OdbcDsn Set-Partition Set-PcsvDeviceBootConfiguration
        Set-PcsvDeviceNetworkConfiguration Set-PcsvDeviceUserPassword Set-PhysicalDisk
        Set-PrintConfiguration Set-Printer Set-PrinterProperty Set-PSCurrentConfigurationNode
        Set-PSDefaultConfigurationDocument Set-PSMetaConfigDocInsProcessedBeforeMeta
        Set-PSMetaConfigVersionInfoV2 Set-PSRepository Set-PSTopConfigurationName Set-ResiliencySetting
        Set-ScheduledTask Set-SmbBandwidthLimit Set-SmbClientConfiguration Set-SmbPathAcl
        Set-SmbServerConfiguration Set-SmbShare Set-StorageFileServer Set-StorageHealthSetting
        Set-StoragePool Set-StorageProvider Set-StorageSetting Set-StorageSubSystem Set-StorageTier
        Set-VirtualDisk Set-Volume Set-VolumeScrubPolicy Set-VpnConnection
        Set-VpnConnectionIPsecConfiguration Set-VpnConnectionProxy
        Set-VpnConnectionTriggerDnsConfiguration Set-VpnConnectionTriggerTrustedNetwork
        Show-NetFirewallRule Show-NetIPsecRule Show-StorageHistory Show-VirtualDisk
        Start-AppBackgroundTask Start-AutologgerConfig Start-EtwTraceSession Start-MpScan Start-MpWDOScan
        Start-NetEventSession Start-PcsvDevice Start-ScheduledTask Start-StorageDiagnosticLog Start-Trace
        Start-WUScan Stop-EtwTraceSession Stop-NetEventSession Stop-PcsvDevice Stop-ScheduledTask
        Stop-StorageDiagnosticLog Stop-StorageJob Stop-Trace StrongConnect Suspend-BitLocker
        Suspend-PrintJob Sync-NetIPsecRule TabExpansion2 Test-ConflictingResources
        Test-ModuleReloadRequired Test-MofInstanceText Test-NetConnection Test-NodeManager
        Test-NodeResources Test-NodeResourceSource Test-ScriptFileInfo ThrowError Unblock-FileShareAccess
        Unblock-SmbShareAccess Uninstall-Module Uninstall-Script Unlock-BitLocker
        Unregister-AppBackgroundTask Unregister-ClusteredScheduledTask Unregister-PSRepository
        Unregister-ScheduledTask Unregister-StorageSubsystem Update-AutologgerConfig
        Update-ConfigurationDocumentRef Update-ConfigurationErrorCount Update-DependsOn Update-Disk
        Update-EtwTraceSession Update-HostStorageCache Update-LocalConfigManager Update-Module
        Update-ModuleManifest Update-ModuleVersion Update-MpSignature
        Update-NetFirewallDynamicKeywordAddress Update-NetIPsecRule Update-Script Update-ScriptFileInfo
        Update-SmbMultichannelConnection Update-StorageFirmware Update-StoragePool
        Update-StorageProviderCache ValidateNoCircleInNodeResources ValidateNodeExclusiveResources
        ValidateNodeManager ValidateNodeResources ValidateNodeResourceSource ValidateNoNameNodeResources
        ValidateUpdate-ConfigurationData Write-Log Write-MetaConfigFile Write-NodeMOFFile
        Write-PrinterNfcTag Write-VolumeCache WriteFile
        """),
        ('User1', 4, ''),
        ('DocComment', 5, ''),
    ),
    stc.STC_LEX_PROPERTIES: (),
    stc.STC_LEX_PYTHON: (
        ('Keywords', 0,
        ' '.join(keyword.kwlist)),  # + ' self doc mb tb sb'
        ('Highlighted identifiers', 1, ' '.join(dir(builtins)) + ' self join split'),
    ),
    stc.STC_LEX_RUBY: (
        ('Keywords', 0, ''),
    ),
    stc.STC_LEX_SQL: (
        ('Keywords', 0,
        """
        access add all alter and any as asc audit between by char check cluster column comment
        compress connect create current date decimal default delete desc distinct drop else
        exclusive exists file float for from grant group having identified immediate in increment
        index initial insert integer intersect into is level like lock long maxextents minus
        mlslabel mode modify noaudit nocompress not nowait null number of offline on online
        option or order pctfree prior public raw rename resource revoke row rowid rownum rows
        select session set share size smallint start successful synonym sysdate table then to
        trigger uid union unique update user validate values varchar varchar2 view whenever
        where with
        """),
        ('Database Objects', 1, ''),
        ('PLDoc', 2, ''),
        ('SQL*Plus', 3,
        """
        / @ @@ accept append archive attribute break btitle center change clear column compute
        connect copy define del describe disconnect edit execute exit exit format get heading
        help host input list log noprint number oserror password pause print prompt recover
        remark repfooter repheader right run save set show shutdown skip spool sqlerror start
        startup store timing ttitle undefine variable whenever whenever xquery
        """),
        ('Oracle functions', 4,
        """
        abs acos add_months appendchildxml approx_count_distinct ascii asciistr asin atan atan2 avg
        bfilename bin_to_num bitand cardinality cast ceil chartorowid chr cluster_details
        cluster_distance cluster_id cluster_probability cluster_set coalesce collect compose
        con_dbid_to_id con_guid_to_id con_name_to_id con_uid_to_id concat convert corr cos cosh
        count covar_pop covar_samp cube_table cume_dist current_date current_timestamp cv
        dataobj_to_mat_partition dataobj_to_partition dbtimezone decode decompose deletexml
        dense_rank depth deref dump empty_blob empty_clob existsnode exp extract extractvalue
        feature_details feature_id feature_set feature_value first first_value floor from_tz
        greatest group_id grouping grouping_id hextoraw initcap insertchildxml insertchildxmlafter
        insertchildxmlbefore insertxmlafter insertxmlbefore instr iteration_number json_query
        json_table json_value lag last last_day last_value lead least length listagg ln lnnvl
        localtimestamp log lower lpad ltrim make_ref max median min mod months_between nanvl nchr
        new_time next_day nls_charset_decl_len nls_charset_id nls_charset_name nls_initcap nls_lower
        nls_upper nlssort nth_value ntile nullif numtodsinterval numtoyminterval nvl nvl2
        ora_dst_affected ora_dst_convert ora_dst_error ora_hash ora_invoking_user
        ora_invoking_userid path percent_rank percentile_cont percentile_disc power powermultiset
        powermultiset_by_cardinality prediction prediction_bounds prediction_cost prediction_details
        prediction_probability prediction_set presentnnv presentv previous rank ratio_to_report
        rawtohex rawtonhex ref reftohex regexp_count regexp_instr regexp_replace regexp_substr
        remainder replace round row_number rowidtochar rowidtonchar rpad rtrim scn_to_timestamp
        sessiontimezone set sign sin sinh soundex sqrt standard_hash stats_binomial_test
        stats_crosstab stats_f_test stats_ks_test stats_mode stats_mw_test stats_one_way_anova
        stats_wsr_test stddev stddev_pop stddev_samp substr sum sys_connect_by_path sys_context
        sys_dburigen sys_extract_utc sys_guid sys_op_zone_id sys_typeid sys_xmlagg sys_xmlgen
        sysdate systimestamp tan tanh timestamp_to_scn to_binary_double to_binary_float to_blob
        to_char to_clob to_date to_dsinterval to_lob to_multi_byte to_nchar to_nclob to_number
        to_single_byte to_timestamp to_timestamp_tz to_yminterval translate treat trim trunc
        tz_offset uid unistr updatexml upper user userenv value var_pop var_samp variance vsize
        width_bucket xmlagg xmlcast xmlcdata xmlcolattval xmlcomment xmlconcat xmldiff xmlelement
        xmlexists xmlforest xmlisvalid xmlparse xmlpatch xmlpi xmlquery xmlroot xmlsequence
        xmlserialize xmltable xmltransform
        """),
        ('User Keywords 2', 5, ''),
        ('User Keywords 3', 6, ''),
        ('User Keywords 4', 7, ''),
    ),
    stc.STC_LEX_TCL: (
        ('TCL Keywords', 0, ''),
        ('TK Keywords', 1, ''),
        ('iTCL Keywords', 2, ''),
        ('tkCommands', 3, ''),
        ('expanduser1', 4, ''),
        ('user2', 5, ''),
        ('user3', 6, ''),
        ('user4', 7, ''),
    ),
    stc.STC_LEX_XML: (
        ('HTML elements and attributes', 0, ''),
        ('JavaScript keywords', 1, ''),
        ('VBScript keywords', 2, ''),
        ('Python keywords', 3, ''),
        ('PHP keywords', 4, ''),
        ('SGML and DTD keywords', 5, ''),
    ),
    stc.STC_LEX_YAML: (
        ('Keywords', 0,
        """
        """),
    ),
    stc.STC_LEX_NULL: (),
}

# # generic keywords
# bash_keywords1 = """
#                  alias ar asa awk banner basename bash bc bdiff break
#                  bunzip2 bzip2 cal calendar case cat cc cd chmod cksum
#                  clear cmp col comm compress continue cp cpio crypt
#                  csplit ctags cut date dc dd declare deroff dev df
#                  diff diff3 dircmp dirname do done du echo ed egrep
#                  elif else env esac eval ex exec exit expand export
#                  expr false fc fgrep fi file find fmt fold for
#                  function functions getconf getopt getopts grep gres
#                  hash head help history iconv id if in integer jobs
#                  join kill local lc less let line ln logname look ls
#                  m4 mail mailx make man mkdir more mt mv newgrp nl nm
#                  nohup ntps od pack paste patch pathchk pax pcat perl
#                  pg pr print printf ps pwd read readonly red return rev
#                  rm rmdir sed select set sh shift size sleep sort spell
#                  split start stop strings strip stty sum suspend sync
#                  tail tar tee test then time times touch tr trap true
#                  tsort tty type typeset ulimit umask unalias uname
#                  uncompress unexpand uniq unpack unset until uudecode
#                  uuencode vi vim vpax wait wc whence which while who
#                  wpaste wstart xargs zcat
#                  """

# # additional keywords from coreutils
# bash_keywords2 = """
#                  chgrp chown chroot dir dircolors factor groups hostid
#                  install link md5sum mkfifo mknod nice pinky printenv
#                  ptx readlink seq sha1sum shred stat su tac unlink
#                  users vdir whoami yes
#                  """

#FIX, create unique/sorted keyword list
# LANG_KWRD['BASH'] += bash_keywords1 + bash_keywords2
# print(LANG_KWRD['BASH'].split())

# preview source code snippets per lexer
#        0:source code
LANG_PRVW = {
    stc.STC_LEX_BASH: (
    """
"""),
    stc.STC_LEX_BATCH: (
    """
@ECHO OFF
CLS

:# application settings
SET PYTHON=python
SET AppPath=D:\\Dev\\D\\wx\\TSN_SPyE
SET AppName=SPyE
SET AppExt=.py
SET AppFile=%AppPath%\\src\\%AppName%%AppExt%
SET PycFile=%AppPath%\\src\\%AppName%.pyc
SET DbgFile=
SET ConfSrc=%AppPath%\\test\\config\\SPyE - TEST.cfg
SET ConfDst=%AppPath%\\src\\config\\%AppName%.cfg

PUSHD %AppPath%

ECHO.
IF "%1"=="--CopyTestCfg" (
  ECHO Running %AppName% with TEST Configuration File
  COPY /Y "%ConfSrc%" "%ConfDst%" >NUL 2>&1
) ELSE (
    IF "%1"=="--DebugWinPDB" (
      ECHO Running %AppName% with WinPDB, GUI for RPDB2 ^(The Remote Python Debugger^)
      SET DbgFile=%AppPath%\\test\\winpdb\\winpdb.py
    ) ELSE (
        ECHO Running %AppName% with Last Saved Configuration File
    )
)
ECHO.

:# try changing .py in .pyw extension
IF NOT EXIST %AppFile% (
    SET AppFile=%AppFile%w
    SET PYTHON=%PYTHON%w
)

%PYTHON% %DbgFile% %AppFile%

POPD

:# clean up .pyc file and RPDB2 console window after debugging
IF EXIST "%PycFile%" DEL /Q /F "%PycFile%"
TASKKILL /FI "WINDOWTITLE eq rpdb2*" >NUL 2>&1
"""),
    stc.STC_LEX_CONF: (
    """
"""),
    stc.STC_LEX_CPP: (
    """
#include <stdio.h>

int main(void)
{
    printf("hello, world\\n");
}
"""),
    stc.STC_LEX_CSS: (
    """
"""),
    stc.STC_LEX_HTML: (
    """
"""),
    stc.STC_LEX_MARKDOWN: (
    """
"""),
    stc.STC_LEX_PASCAL: (
    """
{ Syntax Highlighting Test File for Pascal (copied from Editra)
  Comments are like this
  Hello World in Pascal
}
program Hello;

uses
   crt;

begin
   ClrScr;
   _write('Hello world');
   Readln;
end.

program Variables;

const
   pi: Real = 3.14;

var
   Num1, Num2, Ans: Integer;

begin
   Ans := 1 + 1;
   Num1 := 5;
   Ans := Num1 + 3;
   Num2 := 2;
   Ans := Num1 - Num2;
   Ans := Ans * Num1;
end.
"""),
    stc.STC_LEX_PERL: (
    """
LINE: while (defined($line = <ARGV>)) {
    chomp($line);
    if ($line =~ s/\\$//) {
        $line .= <ARGV>;
        redo LINE unless eof(); # not eof(ARGV)!
    }
    # now process $line
}
"""),
    stc.STC_LEX_PHPSCRIPT: (
    """
"""),
    stc.STC_LEX_POWERSHELL: (
    """
"""),
    stc.STC_LEX_PROPERTIES: (
    """
"""),
    stc.STC_LEX_PYTHON: (
    """
# line comment
class ClassName(kwarg1='text', kwarg2=None):
    '''docstring'''
    \"\"\"docstring\"\"\"
    self.num = 99
    self.string = 'string'
    self.text = "text"
    res = class_method(self.num)
    print(res)
    def class_method(self, arg):
        return arg**arg
"""),
    stc.STC_LEX_RUBY: (
    """
"""),
    stc.STC_LEX_SQL: (
    """
SELECT DECODE(SUM(ABS(gets+immediate_gets)),     0, 1, SUM(ABS(gets+immediate_gets))),
       DECODE(SUM(ABS(misses+immediate_misses)), 0, 1, SUM(ABS(misses+immediate_misses))),
       DECODE(SUM(ABS(sleeps)),                  0, 1, SUM(ABS(sleeps)))
  INTO :v_total_gets, :v_total_misses, :v_total_sleeps
  FROM v$latch;
"""),
    stc.STC_LEX_TCL: (
    """
"""),
    stc.STC_LEX_XML: (
    """
"""),
    stc.STC_LEX_YAML: (
    """
"""),
    stc.STC_LEX_NULL: (
    f"""{LOREM_IPSUM}
"""),
}

#DONE, make labels unique within lexer dict key
#TODO, finish labels and styles, use below URLs as base

#INFO, URL=D:\Dev\U\npp\stylers.xml
#INFO, URL=D:\Dev\D\wx\TSN_SPyE\_SRCREF-TSN-Python-Editor\TSNmod\TSNmod-UliPad-4.2\mixins\LexerBase.py
#INFO, URL=D:\Dev\D\wx\TSN_SPyE\_SRCREF-TSN-Python-Editor\TSNmod\TSNmod-UliPad-4.2\mixins\SyntaxDialog.py
#INFO, URL=D:\Dev\D\wx\TSN_SPyE\_SRCREF-TSN-Python-Editor\TSNmod\TSNmod-DrPython_3.11.4\drPrefsDialog.py
#INFO, URL=D:\Dev\D\wx\TSN_SPyE\_SRCREF-TSN-Python-Editor\TSNmod\TSNmod-DrPython_3.11.4\drStyleDialog.py

#NOTE, currently active: BASH, BATCH, CONF, CPP, PROPERTIES, PYTHON, SQL, TEXT
#NOTE, workaround: changed LANG_STYL to 'list of lists'
# default styles per lexer
#        0:label                        1:token (stylenum)                    2:style
LANG_STYL = {
    stc.STC_LEX_BASH: (
        ('Default',                     stc.STC_SH_DEFAULT,                   'fore:#DD00DD',),
        ('Backtick',                    stc.STC_SH_BACKTICKS,                 'fore:#888888',),
        ('String single quoted',        stc.STC_SH_CHARACTER,                 'fore:#000000',),
        ('Comment',                     stc.STC_SH_COMMENTLINE,               'fore:#303030',),
        ('Error',                       stc.STC_SH_ERROR,                     'fore:#FF0000',),
        ('Heredoc delimiter',           stc.STC_SH_HERE_DELIM,                'fore:#0000FF,bold',),
        ('Heredoc quoted',              stc.STC_SH_HERE_Q,                    'fore:#0000FF,bold',),
        ('Identifier',                  stc.STC_SH_IDENTIFIER,                'fore:#FF0000',),
        ('Number',                      stc.STC_SH_NUMBER,                    'fore:#FF8080',),
        ('Operator',                    stc.STC_SH_OPERATOR,                  'fore:#00C0C0',),
        ('${parameter}',                stc.STC_SH_PARAM,                     'fore:#FF8800',),
        ('Variable',                    stc.STC_SH_SCALAR,                    'fore:#FF0000',),
        ('String double quoted',        stc.STC_SH_STRING,                    'fore:#FFFF80',),
        ('Keyword',                     stc.STC_SH_WORD,                      'fore:#00FF00',),
    ),
    stc.STC_LEX_BATCH: (
        ('Default',                     stc.STC_BAT_DEFAULT,                  'fore:#006400',),
        ('External command',            stc.STC_BAT_COMMAND,                  'fore:#FF0000',),
        ('Comment',                     stc.STC_BAT_COMMENT,                  'fore:#006400,bold',),
        ('Hide command (@)',            stc.STC_BAT_HIDE,                     'fore:#0000FF,bold',),
        ('Identifier',                  stc.STC_BAT_IDENTIFIER,               'fore:#FF0000',),
        ('Jump label',                  stc.STC_BAT_LABEL,                    'bold,fore:#006400,back:#E6F2FF',),
        ('Operator',                    stc.STC_BAT_OPERATOR,                 'fore:#000000,bold',),
        ('Keyword',                     stc.STC_BAT_WORD,                     'fore:#0000FF,bold',),
    ),
    stc.STC_LEX_CONF: (
        ('Default',                     stc.STC_CONF_DEFAULT,                 'fore:#FF0000',),
        ('Comment',                     stc.STC_CONF_COMMENT,                 'fore:#006400,bold',),
        ('Directive',                   stc.STC_CONF_DIRECTIVE,               'fore:#0000FF,bold',),
        ('Extension',                   stc.STC_CONF_EXTENSION,               'fore:#FF0000',),
        ('Identifier',                  stc.STC_CONF_IDENTIFIER,              'fore:#FF0000',),
        ('IP address',                  stc.STC_CONF_IP,                      '',),
        ('Number',                      stc.STC_CONF_NUMBER,                  'fore:#FF0000',),
        ('Operator',                    stc.STC_CONF_OPERATOR,                '',),
        ('Parameter',                   stc.STC_CONF_PARAMETER,               '',),
        ('String',                      stc.STC_CONF_STRING,                  'fore:#FF0000',),
    ),
    stc.STC_LEX_CPP: (
        ('Default',                     stc.STC_C_DEFAULT,                    '',),
        ('String single quoted',        stc.STC_C_CHARACTER,                  '',),
        ('Comment 1',                   stc.STC_C_COMMENT,                    '',),
        ('Comment 2',                   stc.STC_C_COMMENTDOC,                 '',),
        ('Comment 3',                   stc.STC_C_COMMENTDOCKEYWORD,          '',),
        ('Comment 4',                   stc.STC_C_COMMENTDOCKEYWORDERROR,     '',),
        ('Comment 5',                   stc.STC_C_COMMENTLINE,                'fore:#00FF00',),
        ('Comment 6',                   stc.STC_C_COMMENTLINEDOC,             '',),
        ('Global class',                stc.STC_C_GLOBALCLASS,                '',),
        ('String hash-quoted',          stc.STC_C_HASHQUOTEDSTRING,           '',),
        ('Identifier',                  stc.STC_C_IDENTIFIER,                 'fore:#0000FF,bold',),
        ('Number',                      stc.STC_C_NUMBER,                     '',),
        ('Operator',                    stc.STC_C_OPERATOR,                   '',),
        ('Preprocessor',                stc.STC_C_PREPROCESSOR,               'fore:#FF0000',),
        ('Preprocessor comment',        stc.STC_C_PREPROCESSORCOMMENT,        '',),
        ('Regular expression',          stc.STC_C_REGEX,                      '',),
        ('String double quoted',        stc.STC_C_STRING,                     '',),
        ('String unclosed at EOL',      stc.STC_C_STRINGEOL,                  '',),
        ('String raw',                  stc.STC_C_STRINGRAW,                  '',),
        ('String triple double quotes', stc.STC_C_TRIPLEVERBATIM,             '',),
        ('UUID',                        stc.STC_C_UUID,                       '',),
        ('Verbatim identifier',         stc.STC_C_VERBATIM,                   '',),
        ('Keyword',                     stc.STC_C_WORD,                       'fore:#0000FF,bold',),
        ('Keyword 2',                   stc.STC_C_WORD2,                      '',),
    ),
    stc.STC_LEX_CSS: (
        ('Default',                     stc.STC_CSS_DEFAULT,                  '',),
        ('Attribute selection',         stc.STC_CSS_ATTRIBUTE,                '',),
        ('Class selector',              stc.STC_CSS_CLASS,                    '',),
        ('Comment',                     stc.STC_CSS_COMMENT,                  '',),
        ('At-rule (@) except @media',   stc.STC_CSS_DIRECTIVE,                '',),
        ('Double quoted strings',       stc.STC_CSS_DOUBLESTRING,             '',),
        ('Other CSS Property',          stc.STC_CSS_EXTENDED_IDENTIFIER,      '',),
        ('Other Pseudoclass',           stc.STC_CSS_EXTENDED_PSEUDOCLASS,     '',),
        ('Other Pseudoelement',         stc.STC_CSS_EXTENDED_PSEUDOELEMENT,   '',),
        ('ID selector',                 stc.STC_CSS_ID,                       '',),
        ('CSS1 Property',               stc.STC_CSS_IDENTIFIER,               '',),
        ('CSS2 Property',               stc.STC_CSS_IDENTIFIER2,              '',),
        ('CSS3 Property',               stc.STC_CSS_IDENTIFIER3,              '',),
        ('Important',                   stc.STC_CSS_IMPORTANT,                '',),
        ('At-rule (@) for @media',      stc.STC_CSS_MEDIA,                    '',),
        ('Operator',                    stc.STC_CSS_OPERATOR,                 '',),
        ('Pseudo class',                stc.STC_CSS_PSEUDOCLASS,              '',),
        ('Pseudo elements',             stc.STC_CSS_PSEUDOELEMENT,            '',),
        ('Single quoted strings',       stc.STC_CSS_SINGLESTRING,             '',),
        ('Selector (HTML tag)',         stc.STC_CSS_TAG,                      '',),
        ('Unknown Property',            stc.STC_CSS_UNKNOWN_IDENTIFIER,       '',),
        ('Unknown Pseudo class',        stc.STC_CSS_UNKNOWN_PSEUDOCLASS,      '',),
        ('Value',                       stc.STC_CSS_VALUE,                    '',),
        ('Variable (SCSS, LESS, HSS)',  stc.STC_CSS_VARIABLE,                 '',),
    ),
    stc.STC_LEX_HTML: (
        # ('Default',                     stc.STC_H_DEFAULT,                    '',),
        # ('Label',                       stc.STC_H_ASP,                        '',),
        # ('Label',                       stc.STC_H_ASPAT,                      '',),
        # ('Label',                       stc.STC_H_ATTRIBUTE,                  '',),
        # ('Label',                       stc.STC_H_ATTRIBUTEUNKNOWN,           '',),
        # ('Label',                       stc.STC_H_CDATA,                      '',),
        # ('Label',                       stc.STC_H_COMMENT,                    '',),
        # ('Label',                       stc.STC_H_DOUBLESTRING,               '',),
        # ('Label',                       stc.STC_H_ENTITY,                     '',),
        # ('Label',                       stc.STC_H_NUMBER,                     '',),
        # ('Label',                       stc.STC_H_OTHER,                      '',),
        # ('Label',                       stc.STC_H_QUESTION,                   '',),
        # ('Label',                       stc.STC_H_SCRIPT,                     '',),
        # ('Label',                       stc.STC_H_SGML_1ST_PARAM,             '',),
        # ('Label',                       stc.STC_H_SGML_1ST_PARAM_COMMENT,     '',),
        # ('Label',                       stc.STC_H_SGML_BLOCK_DEFAULT,         '',),
        # ('Label',                       stc.STC_H_SGML_COMMAND,               '',),
        # ('Label',                       stc.STC_H_SGML_COMMENT,               '',),
        # ('Label',                       stc.STC_H_SGML_DEFAULT,               '',),
        # ('Label',                       stc.STC_H_SGML_DOUBLESTRING,          '',),
        # ('Label',                       stc.STC_H_SGML_ENTITY,                '',),
        # ('Label',                       stc.STC_H_SGML_ERROR,                 '',),
        # ('Label',                       stc.STC_H_SGML_SIMPLESTRING,          '',),
        # ('Label',                       stc.STC_H_SGML_SPECIAL,               '',),
        # ('Label',                       stc.STC_H_SINGLESTRING,               '',),
        # ('Label',                       stc.STC_H_TAG,                        '',),
        # ('Label',                       stc.STC_H_TAGEND,                     '',),
        # ('Label',                       stc.STC_H_TAGUNKNOWN,                 '',),
        # ('Label',                       stc.STC_H_VALUE,                      '',),
        # ('Label',                       stc.STC_H_XCCOMMENT,                  '',),
        # ('Label',                       stc.STC_H_XMLEND,                     '',),
        # ('Label',                       stc.STC_H_XMLSTART,                   '',),
    ),
    stc.STC_LEX_MARKDOWN: (
        ('Default',                     stc.STC_MARKDOWN_DEFAULT,             'fore:#DD00DD',),
        ('Line begin',                  stc.STC_MARKDOWN_LINE_BEGIN,          'fore:#888888',),
        ('Strong 1',                    stc.STC_MARKDOWN_STRONG1,             'fore:#000000',),
        ('Strong 2',                    stc.STC_MARKDOWN_STRONG2,             'fore:#303030',),
        ('Emphasis 1',                  stc.STC_MARKDOWN_EM1,                 'fore:#FF0000',),
        ('Emphasis 2',                  stc.STC_MARKDOWN_EM2,                 'fore:#0000FF,bold',),
        ('Header 1',                    stc.STC_MARKDOWN_HEADER1,             'fore:#0000FF,bold',),
        ('Header 2',                    stc.STC_MARKDOWN_HEADER2,             'fore:#FF0000',),
        ('Header 3',                    stc.STC_MARKDOWN_HEADER3,             'fore:#FF8080',),
        ('Header 4',                    stc.STC_MARKDOWN_HEADER4,             'fore:#00C0C0',),
        ('Header 5',                    stc.STC_MARKDOWN_HEADER5,             'fore:#FF8800',),
        ('Header 6',                    stc.STC_MARKDOWN_HEADER6,             'fore:#FF0000',),
        ('Preformatted',                stc.STC_MARKDOWN_PRECHAR,             'fore:#FFFF80',),
        ('Unordered list',              stc.STC_MARKDOWN_ULIST_ITEM,          'fore:#00FF00',),
        ('Ordered list',                stc.STC_MARKDOWN_OLIST_ITEM,          'fore:#006400',),
        ('Blockquote',                  stc.STC_MARKDOWN_BLOCKQUOTE,          'fore:#FF0000',),
        ('Strikeout',                   stc.STC_MARKDOWN_STRIKEOUT,           'fore:#006400,bold',),
        ('Horizontal rule',             stc.STC_MARKDOWN_HRULE,               'fore:#0000FF,bold',),
        ('Code',                        stc.STC_MARKDOWN_CODE,                'fore:#FF0000',),
        ('Code block',                  stc.STC_MARKDOWN_CODE2,               'bold,fore:#006400,back:#E6F2FF',),
        ('Code bk',                     stc.STC_MARKDOWN_CODEBK,              'fore:#000000,bold',),
        ('Link',                        stc.STC_MARKDOWN_LINK,                'fore:#0000FF,bold',),
    ),
    stc.STC_LEX_PASCAL: (
        ('Default',                     stc.STC_PAS_DEFAULT,                  '',),
        ('Inline Asm',                  stc.STC_PAS_ASM,                      '',),
        ('Character',                   stc.STC_PAS_CHARACTER,                '',),
        ('Comment: { ... }',            stc.STC_PAS_COMMENT,                  '',),
        ('Comment: (* ... *)',          stc.STC_PAS_COMMENT2,                 '',),
        ('Line Comment: // ...',        stc.STC_PAS_COMMENTLINE,              '',),
        ('Hex Number',                  stc.STC_PAS_HEXNUMBER,                '',),
        ('Identifiers',                 stc.STC_PAS_IDENTIFIER,               '',),
        ('Number',                      stc.STC_PAS_NUMBER,                   '',),
        ('Operators',                   stc.STC_PAS_OPERATOR,                 '',),
        ('Preprocessor: {$ ... }',      stc.STC_PAS_PREPROCESSOR,             '',),
        ('Preprocessor: (*$ ... *)',    stc.STC_PAS_PREPROCESSOR2,            '',),
        ('String',                      stc.STC_PAS_STRING,                   '',),
        ('String unclosed at EOL',      stc.STC_PAS_STRINGEOL,                '',),
        ('Keyword',                     stc.STC_PAS_WORD,                     '',),
    ),
    stc.STC_LEX_PERL: (
        ('Default',                         stc.STC_PL_DEFAULT,                   '',),
        ('Array: @var',                     stc.STC_PL_ARRAY,                     'fore:#0000FF',),
        ('Backtick',                        stc.STC_PL_BACKTICKS,                 '',),
        ('Backtick var',                    stc.STC_PL_BACKTICKS_VAR,             '',),
        ('Single quoted string',            stc.STC_PL_CHARACTER,                 '',),
        ('Comment',                         stc.STC_PL_COMMENTLINE,               '',),
        ('Data Section',                    stc.STC_PL_DATASECTION,               '',),
        ('Error',                           stc.STC_PL_ERROR,                     '',),
        ('Format body',                     stc.STC_PL_FORMAT,                    '',),
        ('Format identifier',               stc.STC_PL_FORMAT_IDENT,              '',),
        ('Hash: %var',                      stc.STC_PL_HASH,                      '',),
        ('Heredoc (delimiter)',             stc.STC_PL_HERE_DELIM,                '',),
        ('Heredoc (single quoted, q)',      stc.STC_PL_HERE_Q,                    '',),
        ('Heredoc (double quoted, qq)',     stc.STC_PL_HERE_QQ,                   '',),
        ('Heredoc (double quoted, qq) var', stc.STC_PL_HERE_QQ_VAR,               '',),
        ('Heredoc (backtick, qx)',          stc.STC_PL_HERE_QX,                   '',),
        ('Heredoc (backtick, qx) var',      stc.STC_PL_HERE_QX_VAR,               '',),
        ('Identifier (functions, etc.)',    stc.STC_PL_IDENTIFIER,                '',),
        ('Long Quote (qq, qr, qw, qx)',     stc.STC_PL_LONGQUOTE,                 '',),
        ('Number',                          stc.STC_PL_NUMBER,                    '',),
        ('Operator',                        stc.STC_PL_OPERATOR,                  '',),
        ('POD: at beginning of line',       stc.STC_PL_POD,                       '',),
        ('POD: verbatim paragraphs',        stc.STC_PL_POD_VERB,                  '',),
        ('Preprocessor',                    stc.STC_PL_PREPROCESSOR,              '',),
        ('Symbols / Punctuation',           stc.STC_PL_PUNCTUATION,               '',),
        ('Regex: /re/ or m{re}',            stc.STC_PL_REGEX,                     '',),
        ('Regex: /re/ or m{re} var',        stc.STC_PL_REGEX_VAR,                 '',),
        ('Substitution: s/re/ore/',         stc.STC_PL_REGSUBST,                  '',),
        ('Substitution: s/re/ore/ var',     stc.STC_PL_REGSUBST_VAR,              '',),
        ('Scalar: $var',                    stc.STC_PL_SCALAR,                    '',),
        ('Double quoted string',            stc.STC_PL_STRING,                    '',),
        ('Single quoted string, generic',   stc.STC_PL_STRING_Q,                  '',),
        ('qq: Double quoted string',        stc.STC_PL_STRING_QQ,                 '',),
        ('qq: Double quoted string var',    stc.STC_PL_STRING_QQ_VAR,             '',),
        ('qr: Regex',                       stc.STC_PL_STRING_QR,                 '',),
        ('qr: Regex var',                   stc.STC_PL_STRING_QR_VAR,             '',),
        ('qw: Array',                       stc.STC_PL_STRING_QW,                 '',),
        ('qx: backtick',                    stc.STC_PL_STRING_QX,                 '',),
        ('qx: backtick var',                stc.STC_PL_STRING_QX_VAR,             '',),
        ('Double quoted string var',        stc.STC_PL_STRING_VAR,                '',),
        ('Subroutine prototype',            stc.STC_PL_SUB_PROTOTYPE,             '',),
        ('Symbol table: *var',              stc.STC_PL_SYMBOLTABLE,               '',),
        ('Keyword',                         stc.STC_PL_WORD,                      'fore:#FF0000',),
        ('Translation: tr{}{} y{}{}',       stc.STC_PL_XLAT,                      '',),
    ),
    stc.STC_LEX_PHPSCRIPT: (
        # ('Default',                     stc.STC_HPHP_DEFAULT,                 '',),
        # ('Label',                       stc.STC_HPHP_COMMENT,                 '',),
        # ('Label',                       stc.STC_HPHP_COMMENTLINE,             '',),
        # ('Label',                       stc.STC_HPHP_COMPLEX_VARIABLE,        '',),
        # ('Label',                       stc.STC_HPHP_HSTRING,                 '',),
        # ('Label',                       stc.STC_HPHP_HSTRING_VARIABLE,        '',),
        # ('Label',                       stc.STC_HPHP_NUMBER,                  '',),
        # ('Label',                       stc.STC_HPHP_OPERATOR,                '',),
        # ('Label',                       stc.STC_HPHP_SIMPLESTRING,            '',),
        # ('Label',                       stc.STC_HPHP_VARIABLE,                '',),
        # ('Keyword',                     stc.STC_HPHP_WORD,                    '',),
    ),
    stc.STC_LEX_POWERSHELL: (
        ('Default',                     stc.STC_POWERSHELL_DEFAULT,           'fore:#FF8080',),
        ('Alias',                       stc.STC_POWERSHELL_ALIAS,             'fore:#00C0C0',),
        ('Character',                   stc.STC_POWERSHELL_CHARACTER,         'fore:#FF8800',),
        ('Cmdlet',                      stc.STC_POWERSHELL_CMDLET,            'fore:#FF0000',),
        ('Comment',                     stc.STC_POWERSHELL_COMMENT,           'fore:#FFFF80',),
        ('Commentstream',               stc.STC_POWERSHELL_COMMENTSTREAM,     'fore:#00FF00',),
        ('Function',                    stc.STC_POWERSHELL_FUNCTION,          'fore:#006400',),
        ('Identifier',                  stc.STC_POWERSHELL_IDENTIFIER,        'fore:#FF0000',),
        ('Keyword',                     stc.STC_POWERSHELL_KEYWORD,           'fore:#006400,bold',),
        ('Number',                      stc.STC_POWERSHELL_NUMBER,            'fore:#0000FF,bold',),
        ('Operator',                    stc.STC_POWERSHELL_OPERATOR,          'fore:#FF0000',),
        ('String',                      stc.STC_POWERSHELL_STRING,            'bold,fore:#006400,back:#E6F2FF',),
        ('User1',                       stc.STC_POWERSHELL_USER1,             'fore:#000000,bold',),
        ('Variable',                    stc.STC_POWERSHELL_VARIABLE,          'fore:#0000FF,bold',),
    ),
    stc.STC_LEX_PROPERTIES: (
        ('Default',                     stc.STC_PROPS_DEFAULT,                'fore:#7F0000',),
        ('Assignment',                  stc.STC_PROPS_ASSIGNMENT,             'fore:#FF0000',),
        ('Comment',                     stc.STC_PROPS_COMMENT,                'fore:#008000',),
        ('Default value',               stc.STC_PROPS_DEFVAL,                 'fore:#7F0000',),
        ('Key name',                    stc.STC_PROPS_KEY,                    'fore:#0000FF',),
        ('Section',                     stc.STC_PROPS_SECTION,                'bold,fore:#FF0000,back:#FFD24D,eol,italic,underline',),
    ),
    stc.STC_LEX_PYTHON: (
        ('Default',                     stc.STC_P_DEFAULT,                    'fore:#000000,face:%(helv)s,size:%(size)d' % FACES,),
        ('String single quoted',        stc.STC_P_CHARACTER,                  'fore:#CF0000,face:%(helv)s,size:%(size)d' % FACES,),
        ('Class name',                  stc.STC_P_CLASSNAME,                  'fore:#0000FF,bold,underline,size:%(size)d' % FACES,),
        ('Comment 1',                   stc.STC_P_COMMENTBLOCK,               'fore:#7F7F7F,size:%(size)d' % FACES,),
        ('Comment 2',                   stc.STC_P_COMMENTLINE,                'fore:#007F00,face:%(other)s,size:%(size)d' % FACES,),
        ('Function name',               stc.STC_P_DEFNAME,                    'fore:#007F7F,bold,size:%(size)d' % FACES,),
        ('Identifier',                  stc.STC_P_IDENTIFIER,                 'fore:#0000FF,face:%(helv)s,size:%(size)d' % FACES,),
        ('Number',                      stc.STC_P_NUMBER,                     'fore:#007F7F,size:%(size)d' % FACES,),
        ('Operator',                    stc.STC_P_OPERATOR,                   'fore:#D66100,bold,size:%(size)d' % FACES,),
        ('String double quoted',        stc.STC_P_STRING,                     'fore:#7F007F,face:%(helv)s,size:%(size)d' % FACES,),
        ('String double quoted at EOL', stc.STC_P_STRINGEOL,                  'fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d' % FACES,),
        ('String triple single quotes', stc.STC_P_TRIPLE,                     'fore:#7F0000,size:%(size)d' % FACES,),
        ('String triple double quotes', stc.STC_P_TRIPLEDOUBLE,               'fore:#7F0000,size:%(size)d' % FACES,),
        ('Keyword',                     stc.STC_P_WORD,                       'fore:#00007F,bold,size:%(size)d' % FACES,),
        ('Keyword 2',                   stc.STC_P_WORD2,                      'fore:#FF40FF,bold,size:%(size)d' % FACES,),
    ),
    stc.STC_LEX_RUBY: (
        # ('Default',                     stc.STC_RB_DEFAULT,                   '',),
        # ('Label',                       stc.STC_RB_BACKTICKS,                 '',),
        # ('Label',                       stc.STC_RB_CHARACTER,                 '',),
        # ('Label',                       stc.STC_RB_CLASSNAME,                 '',),
        # ('Label',                       stc.STC_RB_CLASS_VAR,                 '',),
        # ('Label',                       stc.STC_RB_COMMENTLINE,               '',),
        # ('Label',                       stc.STC_RB_DATASECTION,               '',),
        # ('Label',                       stc.STC_RB_DEFNAME,                   '',),
        # ('Label',                       stc.STC_RB_ERROR,                     '',),
        # ('Label',                       stc.STC_RB_GLOBAL,                    '',),
        # ('Label',                       stc.STC_RB_HERE_DELIM,                '',),
        # ('Label',                       stc.STC_RB_HERE_Q,                    '',),
        # ('Label',                       stc.STC_RB_HERE_QQ,                   '',),
        # ('Label',                       stc.STC_RB_HERE_QX,                   '',),
        # ('Label',                       stc.STC_RB_IDENTIFIER,                '',),
        # ('Label',                       stc.STC_RB_INSTANCE_VAR,              '',),
        # ('Label',                       stc.STC_RB_MODULE_NAME,               '',),
        # ('Label',                       stc.STC_RB_NUMBER,                    '',),
        # ('Label',                       stc.STC_RB_OPERATOR,                  '',),
        # ('Label',                       stc.STC_RB_POD,                       '',),
        # ('Label',                       stc.STC_RB_REGEX,                     '',),
        # ('Label',                       stc.STC_RB_STDERR,                    '',),
        # ('Label',                       stc.STC_RB_STDIN,                     '',),
        # ('Label',                       stc.STC_RB_STDOUT,                    '',),
        # ('Label',                       stc.STC_RB_STRING,                    '',),
        # ('Label',                       stc.STC_RB_STRING_Q,                  '',),
        # ('Label',                       stc.STC_RB_STRING_QQ,                 '',),
        # ('Label',                       stc.STC_RB_STRING_QR,                 '',),
        # ('Label',                       stc.STC_RB_STRING_QW,                 '',),
        # ('Label',                       stc.STC_RB_STRING_QX,                 '',),
        # ('Label',                       stc.STC_RB_SYMBOL,                    '',),
        # ('Label',                       stc.STC_RB_UPPER_BOUND,               '',),
        # ('Keyword',                     stc.STC_RB_WORD,                      '',),
        # ('Label',                       stc.STC_RB_WORD_DEMOTED,              '',),
    ),
    stc.STC_LEX_SQL: (
        ('Default',                     stc.STC_SQL_DEFAULT,                  'fore:#000000',),
        ('String single quoted',        stc.STC_SQL_CHARACTER,                'fore:#FF0000',),
        ('Comment 1',                   stc.STC_SQL_COMMENT,                  'fore:#00FF00',),
        ('Comment 2',                   stc.STC_SQL_COMMENTDOC,               'fore:#000000',),
        ('Comment 3',                   stc.STC_SQL_COMMENTDOCKEYWORD,        'fore:#000000',),
        ('Comment 4',                   stc.STC_SQL_COMMENTDOCKEYWORDERROR,   'fore:#000000',),
        ('Comment 5',                   stc.STC_SQL_COMMENTLINE,              'fore:#00FF00',),
        ('Comment 6',                   stc.STC_SQL_COMMENTLINEDOC,           'fore:#000000',),
        ('Identifier',                  stc.STC_SQL_IDENTIFIER,               'fore:#0F0FFF',),
        ('Number',                      stc.STC_SQL_NUMBER,                   'fore:#FF0000',),
        ('Operator',                    stc.STC_SQL_OPERATOR,                 'fore:#00FF00,bold',),
        ('MySQL identifier',            stc.STC_SQL_QUOTEDIDENTIFIER,         'fore:#000000',),
        ('SQL*Plus keyword',            stc.STC_SQL_SQLPLUS,                  'fore:#0000FF,bold',),
        ('SQL*Plus comment',            stc.STC_SQL_SQLPLUS_COMMENT,          'fore:#00FF00',),
        ('SQL*Plus prompt',             stc.STC_SQL_SQLPLUS_PROMPT,           'fore:#00FFFF',),
        ('String double quoted',        stc.STC_SQL_STRING,                   'fore:#FF0000',),
        ('Oracle function',             stc.STC_SQL_USER1,                    'fore:#FF40FF,bold',),
        ('User keyword 2',              stc.STC_SQL_USER2,                    'fore:#000000',),
        ('User keyword 3',              stc.STC_SQL_USER3,                    'fore:#000000',),
        ('User keyword 4',              stc.STC_SQL_USER4,                    'fore:#000000',),
        ('Keyword',                     stc.STC_SQL_WORD,                     'fore:#008040,bold',),
        ('Keyword 2',                   stc.STC_SQL_WORD2,                    'fore:#000000',),
    ),
    stc.STC_LEX_TCL: (
        # ('Default',                     stc.STC_TCL_DEFAULT,                  '',),
        # ('Label',                       stc.STC_TCL_BLOCK_COMMENT,            '',),
        # ('Label',                       stc.STC_TCL_COMMENT,                  '',),
        # ('Label',                       stc.STC_TCL_COMMENTLINE,              '',),
        # ('Label',                       stc.STC_TCL_COMMENT_BOX,              '',),
        # ('Label',                       stc.STC_TCL_EXPAND,                   '',),
        # ('Label',                       stc.STC_TCL_IDENTIFIER,               '',),
        # ('Label',                       stc.STC_TCL_IN_QUOTE,                 '',),
        # ('Label',                       stc.STC_TCL_MODIFIER,                 '',),
        # ('Label',                       stc.STC_TCL_NUMBER,                   '',),
        # ('Label',                       stc.STC_TCL_OPERATOR,                 '',),
        # ('Label',                       stc.STC_TCL_SUBSTITUTION,             '',),
        # ('Label',                       stc.STC_TCL_SUB_BRACE,                '',),
        # ('Keyword',                     stc.STC_TCL_WORD,                     '',),
        # ('Keyword 2',                   stc.STC_TCL_WORD2,                    '',),
        # ('Keyword 3',                   stc.STC_TCL_WORD3,                    '',),
        # ('Keyword 4',                   stc.STC_TCL_WORD4,                    '',),
        # ('Keyword 5',                   stc.STC_TCL_WORD5,                    '',),
        # ('Keyword 6',                   stc.STC_TCL_WORD6,                    '',),
        # ('Keyword 7',                   stc.STC_TCL_WORD7,                    '',),
        # ('Keyword 8',                   stc.STC_TCL_WORD8,                    '',),
        # ('Label',                       stc.STC_TCL_WORD_IN_QUOTE,            '',),
    ),
    stc.STC_LEX_XML: (
        ('ASP',                         stc.STC_H_ASP,                        'fore:#000000,face:Courier New,size:10',),
        ('ASP at',                      stc.STC_H_ASPAT,                      'fore:#CF0000,face:Courier New,size:10',),
        ('attribute',                   stc.STC_H_ATTRIBUTE,                  'fore:#0000FF,bold,underline,size:10',),
        ('attribute unknown',           stc.STC_H_ATTRIBUTEUNKNOWN,           'fore:#7F7F7F,size:10',),
        ('CData',                       stc.STC_H_CDATA,                      'fore:#007F00,face:Consolas,size:10',),
        ('Double string',               stc.STC_H_DOUBLESTRING,               'fore:#007F7F,bold,size:10',),
        ('Entity',                      stc.STC_H_ENTITY,                     'fore:#0000FF,face:Courier New,size:10',),
        ('Number',                      stc.STC_H_NUMBER,                     'fore:#007F7F,size:10',),
        ('Other',                       stc.STC_H_OTHER,                      'fore:#D66100,bold,size:10',),
        ('Question',                    stc.STC_H_QUESTION,                   'fore:#7F007F,face:Courier New,size:10',),
        ('Script',                      stc.STC_H_SCRIPT,                     'fore:#000000,face:Courier New,back:#E0C0E0,eol,size:10',),
        ('Single string',               stc.STC_H_SINGLESTRING,               'fore:#7F0000,size:10',),
        ('Tag',                         stc.STC_H_TAG,                        'fore:#7F0000,size:10',),
        ('Tag end',                     stc.STC_H_TAGEND,                     'fore:#00007F,bold,size:10',),
        ('Tag unknown',                 stc.STC_H_TAGUNKNOWN,                 'fore:#FF40FF,bold,size:10',),
        ('Value',                       stc.STC_H_VALUE,                      'fore:#0000FF,bold',),
        ('XC Comment',                  stc.STC_H_XCCOMMENT,                  'fore:#FF0000',),
        ('XML end',                     stc.STC_H_XMLEND,                     'bold,fore:#006400,back:#E6F2FF',),
        ('XML start',                   stc.STC_H_XMLSTART,                   'fore:#000000,bold',),
    ),
    stc.STC_LEX_YAML: (
        ('Default',                     stc.STC_YAML_DEFAULT,                 'fore:#7F0000',),
        ('Label',                       stc.STC_YAML_COMMENT,                 'fore:#FF0000',),
        ('Number',                      stc.STC_YAML_NUMBER,                  'fore:#008000',),
        ('Reference',                   stc.STC_YAML_REFERENCE,               'fore:#7F0000',),
        ('Document',                    stc.STC_YAML_DOCUMENT,                'fore:#0000FF',),
        ('Text',                        stc.STC_YAML_TEXT,                    'bold,fore:#FF0000,back:#FFD24D,eol,italic,underline',),
        ('Error',                       stc.STC_YAML_ERROR,                   'bold,fore:#006400,back:#E6F2FF',),
        ('Identifier',                  stc.STC_YAML_IDENTIFIER,              'bold,fore:#006400,back:#000000',),
        ('Keyword',                     stc.STC_YAML_KEYWORD,                 'fore:#00FF00,bold',),
        ('Operator',                    stc.STC_YAML_OPERATOR,                'bold,fore:#006400,back:#FFFFFF',),
    ),
    stc.STC_LEX_NULL: (
        ('Default',                     0,                                    '',),
    ),
}

#TODO, test effect of property value changes
# properties per lexer (taken from SciTE)
#        0:name          1:value
LANG_PROP = {
    stc.STC_LEX_BASH: (
        ('fold.comment', '1'),
        ('fold.compact', '1'),
    ),
    stc.STC_LEX_BATCH: (),
    stc.STC_LEX_CONF: (),
    stc.STC_LEX_CPP: (
        ('fold',                                     '1'),
        ('fold.at.else',                             '1'),
        ('fold.comment',                             '1'),
        ('fold.compact',                             '1'),
        ('fold.cpp.comment.explicit',                '1'),
        ('fold.cpp.comment.multiline',               '1'),
        ('fold.cpp.explicit.anywhere',               '1'),
        ('fold.cpp.explicit.end',                    '1'),
        ('fold.cpp.explicit.start',                  '1'),
        ('fold.cpp.preprocessor.at.else',            '1'),
        ('fold.cpp.syntax.based',                    '1'),
        ('fold.preprocessor',                        '1'),
        ('lexer.cpp.allow.dollars',                  '0'),
        ('lexer.cpp.backquoted.strings',             '0'),
        ('lexer.cpp.escape.sequence',                '0'),
        ('lexer.cpp.hashquoted.strings',             '0'),
        ('lexer.cpp.track.preprocessor',             '0'),
        ('lexer.cpp.triplequoted.strings',           '0'),
        ('lexer.cpp.update.preprocessor',            '0'),
        ('lexer.cpp.verbatim.strings.allow.escapes', '0'),
        ('styling.within.preprocessor',              '0'),
    ),
    stc.STC_LEX_CSS: (
        ('fold.comment',            '1'),
        ('fold.compact',            '1'),
        ('lexer.css.hss.language',  '0'),
        ('lexer.css.less.language', '0'),
        ('lexer.css.scss.language', '0'),
    ),
    stc.STC_LEX_HTML: (
        ('asp.default.language',     '0'),
        ('fold',                     '0'),
        ('fold.compact',             '0'),
        ('fold.html',                '0'),
        ('fold.html.preprocessor',   '0'),
        ('fold.hypertext.comment',   '0'),
        ('fold.hypertext.heredoc',   '0'),
        ('html.tags.case.sensitive', '0'),
        ('lexer.html.django',        '0'),
        ('lexer.html.mako',          '0'),
        ('lexer.xml.allow.scripts',  '0'),
    ),
    stc.STC_LEX_MARKDOWN: (),
    stc.STC_LEX_PASCAL: (
        ('fold.comment',      '0'),
        ('fold.compact',      '0'),
        ('fold.preprocessor', '0'),
    ),
    stc.STC_LEX_PERL: (
        ('fold',                       '0'),
        ('fold.comment',               '0'),
        ('fold.compact',               '0'),
        ('fold.perl.at.else',          '0'),
        ('fold.perl.comment.explicit', '0'),
        ('fold.perl.package',          '0'),
        ('fold.perl.pod',              '0'),
    ),
    stc.STC_LEX_PHPSCRIPT: (),
    stc.STC_LEX_POWERSHELL: (
        ('fold.at.else', '0'),
        ('fold.comment', '0'),
        ('fold.compact', '0'),
    ),
    stc.STC_LEX_PROPERTIES: (
        ('fold.compact',                     '1'),
        ('lexer.props.allow.initial.spaces', '0'),
    ),
    stc.STC_LEX_PYTHON: (
        ('fold',                   '1'),
        ('fold.quotes.python',     '1'),
        ('tab.timmy.whinge.level', '1'),
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # ('fold',                                      '1'),
        # ('fold.compact',                              '0'),
        # ('fold.quotes.python',                        '1'),
        # ('lexer.python.keywords2.no.sub.identifiers', '0'),
        # ('lexer.python.literals.binary',              '0'),
        # ('lexer.python.strings.b',                    '0'),
        # ('lexer.python.strings.f',                    '0'),
        # ('lexer.python.strings.over.newline',         '0'),
        # ('lexer.python.strings.u',                    '0'),
        # ('lexer.python.unicode.identifiers',          '0'),
        # ('tab.timmy.whinge.level',                    '1'),
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    ),
    stc.STC_LEX_RUBY: (
        ('fold.comment', '0'),
        ('fold.compact', '0'),
    ),
    stc.STC_LEX_SQL: (
        ('fold',                           '0'),
        ('fold.comment',                   '0'),
        ('fold.compact',                   '0'),
        ('fold.sql.at.else',               '0'),
        ('fold.sql.only.begin',            '0'),
        ('lexer.sql.allow.dotted.word',    '0'),
        ('lexer.sql.backticks.identifier', '0'),
        ('lexer.sql.numbersign.comment',   '0'),
        ('sql.backslash.escapes',          '0'),
    ),
    stc.STC_LEX_TCL: (
        ('fold.comment', '0'),
    ),
    stc.STC_LEX_XML: (),
    stc.STC_LEX_YAML: (
        ('fold.comment.yaml', '0'),
    ),
    stc.STC_LEX_NULL: (),
}

#TODO, transform to lexer key, e.g. stc.STC_LEX_PYTHON
# code context block opener keywords per lexer
CCX_BLOCKOPENERS = {
    'BASH'  : [
        'case',
        'do',
        'done',
        'elif',
        'else',
        'esac',
        'fi',
        'for',
        'function',
        'if',
        'select',
        'then',
        'until',
        'while',
        ],
    'PYTHON': [
        'class',
        'def',
        'elif',
        'else',
        'except',
        'finally',
        'for',
        'if',
        'try',
        'while',
        'with',
        ],
}

#TODO, for now, only Python and Bash support
CCX_BLOCKOPENERS = CCX_BLOCKOPENERS['PYTHON']
