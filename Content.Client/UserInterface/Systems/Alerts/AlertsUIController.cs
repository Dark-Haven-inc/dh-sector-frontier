using Content.Client.Alerts;
using Content.Client.Gameplay;
using Content.Client.UserInterface.Systems.Alerts.Widgets;
using Content.Client.UserInterface.Systems.Gameplay;
using Content.Shared.Alert;
using Content.Shared.Lua.CLVar;
using Robust.Client.GameObjects;
using Robust.Client.Player;
using Robust.Client.UserInterface;
using Robust.Client.UserInterface.Controllers;
using Robust.Shared.Configuration;
using Robust.Shared.Prototypes;

namespace Content.Client.UserInterface.Systems.Alerts;

public sealed class AlertsUIController : UIController, IOnStateEntered<GameplayState>, IOnSystemChanged<ClientAlertsSystem>
{
    [Dependency] private readonly IPlayerManager _player = default!;
    [Dependency] private readonly IConfigurationManager _cfg = default!;

    [UISystemDependency] private readonly ClientAlertsSystem? _alertsSystem = default;

    private AlertsUI? UI => UIManager.GetActiveUIWidgetOrNull<AlertsUI>();

    public override void Initialize()
    {
        base.Initialize();

        var gameplayStateLoad = UIManager.GetUIController<GameplayStateLoadController>();
        gameplayStateLoad.OnScreenLoad += OnScreenLoad;
        gameplayStateLoad.OnScreenUnload += OnScreenUnload;

        _cfg.OnValueChanged(CLVars.AlertsIconScale, OnAlertsIconScaleChanged, invokeImmediately: true);
    }

    private void OnAlertsIconScaleChanged(float value)
    { UI?.SetIconScale(value); }

    private void OnScreenUnload()
    {
        var widget = UI;
        if (widget != null)
            widget.AlertPressed -= OnAlertPressed;
    }

    private void OnScreenLoad()
    {
        var widget = UI;
        if (widget != null)
        {
            widget.AlertPressed += OnAlertPressed;
            widget.SetIconScale(_cfg.GetCVar(CLVars.AlertsIconScale));
        }

        SyncAlerts();
    }

    private void OnAlertPressed(object? sender, ProtoId<AlertPrototype> e)
    {
        _alertsSystem?.AlertClicked(e);
    }

    private void SystemOnClearAlerts(object? sender, EventArgs e)
    {
        UI?.ClearAllControls();
    }

    private void SystemOnSyncAlerts(object? sender, IReadOnlyDictionary<AlertKey, AlertState> e)
    {
        if (sender is ClientAlertsSystem system)
        {
            UI?.SyncControls(system, system.AlertOrder, e);
        }
    }

    public void OnSystemLoaded(ClientAlertsSystem system)
    {
        system.SyncAlerts += SystemOnSyncAlerts;
        system.ClearAlerts += SystemOnClearAlerts;
    }

    public void OnSystemUnloaded(ClientAlertsSystem system)
    {
        system.SyncAlerts -= SystemOnSyncAlerts;
        system.ClearAlerts -= SystemOnClearAlerts;
    }


    public void OnStateEntered(GameplayState state)
    {
        // initially populate the frame if system is available
        SyncAlerts();
    }

    public void SyncAlerts()
    {
        var alerts = _alertsSystem?.ActiveAlerts;
        if (alerts != null)
        {
            SystemOnSyncAlerts(_alertsSystem, alerts);
        }
    }

    public void UpdateAlertSpriteEntity(EntityUid spriteViewEnt, AlertPrototype alert)
    {
        if (_player.LocalEntity is not { } player)
            return;

        if (!EntityManager.TryGetComponent<SpriteComponent>(spriteViewEnt, out var sprite))
            return;

        var ev = new UpdateAlertSpriteEvent((spriteViewEnt, sprite), player, alert);
        EntityManager.EventBus.RaiseLocalEvent(player, ref ev);
        EntityManager.EventBus.RaiseLocalEvent(spriteViewEnt, ref ev);
    }
}
