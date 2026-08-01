$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

function ConvertFrom-HtmlText([string]$value) {
    $withoutTags = [regex]::Replace($value, '<[^>]+>', ' ')
    $decoded = [System.Net.WebUtility]::HtmlDecode($withoutTags)
    return [regex]::Replace($decoded, '\s+', ' ').Trim()
}

$pages = Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.html' |
    Where-Object {
        $_.Name -match '-(en|es)\.html$' -and $_.Name -notmatch '^search-(en|es)\.html$' -and
        $_.FullName -notmatch '\\(assets|creatives|New format|Revolution|tmp)\\'
    } |
    ForEach-Object {
        $html = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
        $language = if ($_.Name -match '-es\.html$') { 'es' } else { 'en' }
        $titleMatch = [regex]::Match($html, '<title[^>]*>([\s\S]*?)</title>', 'IgnoreCase')
        $title = if ($titleMatch.Success) { ConvertFrom-HtmlText $titleMatch.Groups[1].Value } else { '' }
        $title = [regex]::Replace($title, '\s*[|\u2013-]\s*Mat.as Gaglio.*$', '', 'IgnoreCase')
        $descriptionMatch = [regex]::Match($html, '<meta\s+name=["'']description["'']\s+content=["'']([^"'']*)', 'IgnoreCase')
        $keywordMatch = [regex]::Match($html, '<meta\s+name=["'']keywords["'']\s+content=["'']([^"'']*)', 'IgnoreCase')
        $imageMatch = [regex]::Match($html, '<meta\s+(?:property|name)=["'']og:image["'']\s+content=["'']([^"'']+)', 'IgnoreCase')
        if (-not $imageMatch.Success) { $imageMatch = [regex]::Match($html, '<img[^>]+src=["'']([^"'']+)', 'IgnoreCase') }
        $headings = [regex]::Matches($html, '<h[1-3][^>]*>([\s\S]*?)</h[1-3]>', 'IgnoreCase') | ForEach-Object { ConvertFrom-HtmlText $_.Groups[1].Value }
        $body = [regex]::Replace($html, '<(script|style|svg|header|footer|nav)[^>]*>[\s\S]*?</\1>', ' ', 'IgnoreCase')
        $body = [regex]::Replace($body, '<!--[\s\S]*?-->', ' ')
        $content = ConvertFrom-HtmlText $body
        if ($content.Length -gt 30000) { $content = $content.Substring(0, 30000) }
        $relative = $_.FullName.Substring($root.Length).TrimStart('\').Replace('\', '/')
        $metaKeywords = if ($keywordMatch.Success) { ConvertFrom-HtmlText $keywordMatch.Groups[1].Value } else { '' }

        [ordered]@{
            title = if ($title) { $title } elseif ($headings.Count) { $headings[0] } else { $_.BaseName }
            description = if ($descriptionMatch.Success) { ConvertFrom-HtmlText $descriptionMatch.Groups[1].Value } else { '' }
            keywords = ($metaKeywords + ' ' + ($headings -join ' ')).Trim()
            content = $content
            lang = $language
            url = $relative
            image = if ($imageMatch.Success) { [System.Net.WebUtility]::HtmlDecode($imageMatch.Groups[1].Value) } else { '' }
        }
    }

$json = $pages | ConvertTo-Json -Depth 3 -Compress
[IO.File]::WriteAllText((Join-Path $root 'search-index.json'), $json, [Text.UTF8Encoding]::new($false))
Write-Host "Indexed $($pages.Count) localized pages."
