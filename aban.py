import sys
try:
    import weechat
except ImportError:
    print('This script has to run under WeeChat (https://weechat.org/).')
    sys.exit(1)

SCRIPT_NAME = 'aban'
SCRIPT_AUTHOR = 'NetSysFire'
SCRIPT_VERSION = '0.1'
SCRIPT_LICENSE = 'GPL'
SCRIPT_DESC = 'Script which makes banning/quieting users via account name ($a:) faster'

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', '')

weechat.hook_command("aban", "ban users with $a","[<nick> [<nick>...]]", "nick: the nick to ban", "%(irc_channel_nicks_hosts)", "aban", "")
weechat.hook_command("aquiet", "quiet users with $a","[<nick> [<nick>...]]", "nick: the nick to quiet", "%(irc_channel_nicks_hosts)", "aquiet", "")
weechat.hook_hsignal('irc_redirection_action_who', 'action_cb', '')

PENDING_ACTIONS = {}

def get_buffer(server, channel):
    buffer = weechat.info_get("irc_buffer", f"{server},{channel}")
    return buffer

def log_warning(text):
    weechat.prnt("", f"{weechat.prefix('error')}[aban] {text}")

def aban(data, buffer, arglist):
    for nick in arglist.split(" "):
        prepare_and_send_signal(buffer, nick, "ban")
    return weechat.WEECHAT_RC_OK

def aquiet(data, buffer, arglist):
    for nick in arglist.split(" "):
        prepare_and_send_signal(buffer, nick, "quiet")
    return weechat.WEECHAT_RC_OK

def prepare_and_send_signal(buffer, nick, action):
    global PENDING_ACTIONS
    # needed to get the server buffer (irc.server.#somechannel)
    buffer_info = weechat.buffer_get_string(buffer, "full_name").split(".")
    if buffer_info.pop(0) != "irc":
        log_warning("aban can only be used in irc channel buffers")
        return weechat.WEECHAT_RC_ERROR

    server, channel = buffer_info
    if not channel.startswith("#"):
        log_warning("aban can only be used in irc channel buffers")
        return weechat.WEECHAT_RC_ERROR
    if weechat.info_get('irc_nick', server) == nick:
        log_warning(f"You probably do not want to {action} yourself.")
        return weechat.WEECHAT_RC_ERROR
    # see known issues section in the README
    PENDING_ACTIONS[nick] = {"server": server, "channel": channel, "action": action}

    weechat.hook_hsignal_send("irc_redirect_command", {"server": server, "pattern": "who", "signal": "action"})
    weechat.hook_signal_send('irc_input_send', weechat.WEECHAT_HOOK_SIGNAL_STRING, f"{server};;2;;/who {nick} %a")

    # to please pylint
    return weechat.WEECHAT_RC_OK

def action_cb(msg, signal, hashtable):
    global PENDING_ACTIONS
    identified_nick = hashtable["output"].split("\n")[0].split()[3] # 0 if unidentified
    target_nick = hashtable["output"].split("\n")[1].split()[3]
    if not target_nick in PENDING_ACTIONS:
        log_warning(f"expired ban for {target_nick}?")
        return weechat.WEECHAT_RC_ERROR
    if identified_nick == "0":
        target = target_nick
    else:
        target = f"$a:{identified_nick}"
    buffer = get_buffer(PENDING_ACTIONS[target_nick]["server"], PENDING_ACTIONS[target_nick]["channel"])
    action = PENDING_ACTIONS[target_nick]["action"]

    if action == "ban":
        weechat.command(buffer, f"/ban {target}")
        weechat.command(buffer, f"/kick {target_nick}")
    if action == "quiet":
        weechat.command(buffer, f"/quiet {target}")

    del PENDING_ACTIONS[target_nick]
    return weechat.WEECHAT_RC_OK
