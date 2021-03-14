# aban - banning and quieting people with ease

Are you a chanop using `weechat` in a channel which has the channel mode `+r` set? Are you tired of running `/whois` every time you want to ban someone? Then look no further! aban can save you these precious few seconds.

## Installing

See [the official WeeChat docs](https://weechat.org/files/doc/stable/weechat_user.en.html#scripts_plugins). There are no special steps needed for this script.

## How do I use it?

```
/aban aMisbehavingUser
```

or

```
/aquiet aMisbehavingUser
```

If the user is unidentified the standard mask will be applied as this script is just calling `/ban` and `/quiet`.

*Keep in mind that `/aban` does not only ban the user but it will kick them, too. This does not apply to `/aquiet`.*

## FAQ

### Will this script eat my cat?

This script has been tested. No cats have been eaten (so far). `pylint` has also been run on this script.

### This script ate my cat!

This is unfortunate. Please create an issue for that and append some debug information:

- What IRC network the script was used on
- The `/who <nick> %a` output
- Any errors or warnings you got in the weechat buffer
- Anything else that you think is relevant

### Will this work with my weechat version?

Probably. This script does not use incredibly complex weechat API incantations. It was tested with version `3.0.1`.

### What IRC networks has this been tested with?

freenode, hackint and OFTC. It will work on any other IRC network which has the same behavior for `/who <nick> %a` and supports `$a:`.

### This repo was not touched in a while? Is it dead?

Probably not. Since this project is quite simple it does not need a lot of maintenance and attention.

### What does the "a" in aban stand for?

Basically "authenticated" or "account", also because it works with `$a:`.

## Known issues

### Targeting the same user on multiple servers does not work

Since the only information the callback function gets is the nick and identified nick the script can only look for the nick in the dictionary of pending actions. If you target the same user on different servers simultaneously only one invocation will work and it might get the wrong account name. This is also an edge case.
In order to solve this it is necessary to add more complexity to the script.
