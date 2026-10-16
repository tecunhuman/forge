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

Add the host name to `/etc/hosts`:

```bash
127.0.0.1  forge.lan
```

2. Create the data folders and start the server:

```bash
make init
make server
```

3. Open `http://forge.lan:3000` and create the admin account.

4. Register the runner and start everything:

```bash
make runner-config
make register
make up
```

Command-line provisioning
-------------------------

Create an API token for the Forgejo user that will own and administer the new resources. Export it for the current
shell session so it is not stored on disk:

```bash
export TOKEN=$(./forge-api.py token admin)
```

Create an organization and repositories from the command line:

```bash
./forge-api.py org create tecunhuman --description "Tecunhuman projects"
./forge-api.py repo create tecunhuman/new-project --description "A new project"
./forge-api.py repo create tecunhuman/private-project --private
```

Use just a repository name, without `OWNER/`, to create it under the user associated with `TOKEN`.
Repositories are empty by default; pass `--init` to initialize one with its default branch. Run `./forge-api.py --help`
for all options.

For a single operation, the token can be scoped to only that command:

```bash
TOKEN=$(./forge-api.py token admin) ./forge-api.py repo create tecunhuman/new-project
```

Backups
-------

```bash
make backup
```

Cron example:

```bash
0 3 * * * $HOME/workspace/forge/backup.sh
```
