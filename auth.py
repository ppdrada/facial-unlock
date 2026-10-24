import sys
import threading


def verify_owner(reason):
    """Pede a senha do computador (ou biometria) na janela do próprio sistema.

    Retorna True se o dono confirmou. O app nunca vê a senha.
    """
    if sys.platform == "darwin":
        return _verify_macos(reason)
    if sys.platform == "win32":
        return _verify_windows(reason)
    return False


def _verify_macos(reason):
    # Touch ID ou senha do Mac
    try:
        from LocalAuthentication import LAContext, LAPolicyDeviceOwnerAuthentication
    except ImportError:
        print("Instale pyobjc-framework-LocalAuthentication para pedir a senha.")
        return False

    context = LAContext.alloc().init()
    done = threading.Event()
    result = {"ok": False}

    def reply(success, error):
        result["ok"] = bool(success)
        done.set()

    context.evaluatePolicy_localizedReason_reply_(LAPolicyDeviceOwnerAuthentication, reason, reply)
    done.wait()
    return result["ok"]


def _verify_windows(reason):
    # Windows Hello: PIN, digital, rosto ou senha
    try:
        import asyncio

        from winrt.windows.security.credentials.ui import (
            UserConsentVerificationResult,
            UserConsentVerifier,
            UserConsentVerifierAvailability,
        )
    except ImportError:
        print("Instale winrt-Windows.Security.Credentials.UI para pedir a senha.")
        return False

    async def check():
        available = await UserConsentVerifier.check_availability_async()
        if available != UserConsentVerifierAvailability.AVAILABLE:
            print("Windows Hello não está configurado (crie um PIN nas Configurações).")
            return False
        result = await UserConsentVerifier.request_verification_async(reason)
        return result == UserConsentVerificationResult.VERIFIED

    return asyncio.run(check())
