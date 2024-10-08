# Changelog

## 0.2.0 (2024-10-02)

### Bug fixes

- Update access level mapping after sharinghub-server changes
- Chrome compatibility, injected code via onload was not working

### Features

- UI: Change navbar right links to open in new tab
- UI: Add open button if iframe
- UI: Add refresh button if iframe
- UI: Display links buttons if not in iframe

### Internal

- Improve permissions module

## 0.1.0 (2024-09-09)

### Features

- Register plugin in "mlflow.app" entry-point as "sharinghub"
- Add base mlflow-sharinghub plugin, GitLab integrated, project dispatching
- **Gitlab**: OpenID Connect auth, save access_token, refresh_token, and userinfo in session
- **Gitlab**: Add config for mandatory gitlab topics for projects
- Add SharingHub integration
- **SharingHub**: Use SharingHub session cookie for request
- **SharingHub**: Add config for mandatory stac collection
- Add permission based from GitLab/SharingHub access level
- **UI**: Add link to auth page in ui navbar, add back button in auth page if connected
- **UI**: Display user name and email in auth page
- **UI**: Add home button for project views
- **UI**: Add home button in auth page when under project path
- **UI**: Add read-only tag to global view
- **UI**: Add link to project in gitlab/sharinghub for project views
- **UI**: Force light mode

### Internal

- Create Helm Chart
- Document configuration for GitLab/SharingHub integration
- Write deployment guide
