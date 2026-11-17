/* ARLO STUDIO.exe: starts the bundled Python (runtime\pythonw.exe -m arlo.app) from the
   folder this exe sits in, passing any files given on the command line (or dropped on it). */
#define WIN32_LEAN_AND_MEAN
#define UNICODE
#define _UNICODE
#include <windows.h>
#include <wchar.h>

static const wchar_t *skip_arg0(const wchar_t *cl) {
    if (*cl == L'"') { cl++; while (*cl && *cl != L'"') cl++; if (*cl) cl++; }
    else { while (*cl && *cl != L' ' && *cl != L'\t') cl++; }
    while (*cl == L' ' || *cl == L'\t') cl++;
    return cl;
}

int WINAPI wWinMain(HINSTANCE inst, HINSTANCE prev, PWSTR args, int show) {
    (void)inst; (void)prev; (void)args; (void)show;
    wchar_t dir[MAX_PATH];
    DWORD n = GetModuleFileNameW(NULL, dir, MAX_PATH);
    if (n == 0 || n >= MAX_PATH) return 1;
    wchar_t *slash = wcsrchr(dir, L'\\');
    if (slash) *slash = 0;

    wchar_t py[MAX_PATH + 32];
    swprintf(py, MAX_PATH + 32, L"%s\\runtime\\pythonw.exe", dir);
    if (GetFileAttributesW(py) == INVALID_FILE_ATTRIBUTES) {
        MessageBoxW(NULL, L"The runtime folder is missing. Unzip the whole ARLO STUDIO folder and run ARLO STUDIO.exe from inside it.",
                    L"ARLO STUDIO", MB_ICONERROR);
        return 1;
    }
    const wchar_t *rest = skip_arg0(GetCommandLineW());
    size_t len = wcslen(py) + wcslen(rest) + 64;
    wchar_t *cmd = (wchar_t *)HeapAlloc(GetProcessHeap(), 0, len * sizeof(wchar_t));
    if (!cmd) return 1;
    swprintf(cmd, len, L"\"%s\" -E -s -m arlo.app %s", py, rest);

    SetEnvironmentVariableW(L"PYTHONHOME", NULL);
    SetEnvironmentVariableW(L"PYTHONPATH", NULL);
    STARTUPINFOW si = { sizeof si };
    PROCESS_INFORMATION pi;
    if (!CreateProcessW(py, cmd, NULL, NULL, FALSE, 0, NULL, dir, &si, &pi)) {
        MessageBoxW(NULL, L"ARLO STUDIO could not start its Python runtime.", L"ARLO STUDIO", MB_ICONERROR);
        return 1;
    }
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return 0;
}
