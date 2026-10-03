forge
=====

Local Forgejo and Actions runner for the tecunhuman projects.

Live data is stored in `$FORGE_DATA` and is not backed up directly.  `backup.sh` exports it to this folder:

* `archives/` - forgejo dumps (database, repositories and settings).
* `bundles/` - one git bundle per repository (`git clone <repo>.bundle`).

How to Setup
------------

1. Copy the settings and edit `FORGE_HOST` and `FORGE_DATA`:

```bash
cp .env.example .env
```

2. Create the data folders and start the server:

```bash
make init
make server
```

3. Open `http://$FORGE_HOST:3000` and create the admin account.

4. Register the runner and start everything:

```bash
make runner-config
make register
make up
```

Backups
-------

```bash
make backup
```

Cron example:

```bash
0 3 * * * $HOME/tecunhuman/forge/backup.sh
```
