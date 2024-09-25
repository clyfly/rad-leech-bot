from bot import CMD_SUFFIX as x


class _BotCommands:
    def __init__(self):
        self.StartCommand = f"start"
        self.MirrorCommand = [f"mirror{x}", f"m{x}"]
        self.QbMirrorCommand = [f"qbmirror{x}", f"qbm{x}"]
        self.JdMirrorCommand = [f"jdmirror{x}", f"jdm{x}"]
        self.YtdlCommand = [f"ytdl{x}", f"ytm{x}"]
        self.NzbMirrorCommand = [f"nzbmirror{x}", f"nzm{x}"]
        self.LeechCommand = [f"leech{x}", f"l{x}"]
        self.QbLeechCommand = [f"qbleech{x}", f"qbl{x}"]
        self.JdLeechCommand = [f"jdleech{x}", f"jdl{x}"]
        self.YtdlLeechCommand = [f"ytdlleech{x}", f"ytl{x}"]
        self.NzbLeechCommand = [f"nzbleech{x}", f"nzl{x}"]
        self.CloneCommand = f"clone{x}"
        self.CountCommand = f"count{x}"
        self.SpeedCommand = f"speedtest{x}"
        self.DeleteCommand = f"del{x}"
        self.CancelTaskCommand = f"cancel{x}"
        self.CancelAllCommand = f"cancelall{x}"
        self.ForceStartCommand = [f"forcestart{x}", f"fs{x}"]
        self.ListCommand = f"list{x}"
        self.SearchCommand = f"search{x}"
        self.StatusCommand = f"status{x}"
        self.UsersCommand = f"users{x}"
        self.AuthorizeCommand = f"authorize{x}"
        self.UnAuthorizeCommand = f"unauthorize{x}"
        self.AddSudoCommand = f"addsudo{x}"
        self.RmSudoCommand = f"rmsudo{x}"
        self.PingCommand = f"ping{x}"
        self.RestartCommand = f"restart{x}"
        self.StatsCommand = f"stats{x}"
        self.HelpCommand = f"help{x}"
        self.LogCommand = f"log{x}"
        self.ShellCommand = f"shell{x}"
        self.AExecCommand = f"aexec{x}"
        self.ExecCommand = f"exec{x}"
        self.ClearLocalsCommand = f"clearlocals{x}"
        self.BotSetCommand = [f"bsetting{x}", f"bs{x}"]
        self.UserSetCommand = [f"usetting{x}", f"us{x}"]
        self.SelectCommand = f"sel{x}"
        self.RssCommand = f"rss{x}"


BotCommands = _BotCommands()
