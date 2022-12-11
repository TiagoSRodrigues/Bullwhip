Write-Output "Analysing the code..."

conda activate Bullwhip

Set-Location 'N:\Tese\Bullwhip'
$app_name = 'N:\TESE\Bullwhip'
$export_performance = 'N:\TESE\Bullwhip\data\exports\performance\'

Write-Output "Checking the quality..."
# Code quality
pylint $app_name > $export_performance"quality_metrics_pylint.txt"
flake8 $app_name/ --output-file $export_performance"quality_metrics_flake8.txt"

Write-Output "Checking complexity..."
# Cyclomatic Complexity (CC, HAL, MI) metrics.

Write-Output "MI INDEX\n============\n" > $export_performance"complexity_metrics.txt"
radon mi "$app_name" -s >> $export_performance"complexity_metrics.txt"
Write-Output "\nCC INDEX\n============\n" >> $export_performance"complexity_metrics.txt"
radon cc "$app_name" -a -s -nc >> $export_performance"complexity_metrics.txt"
# Write-Output "\nHAL INDEX\n===========\n" >> $export_performance"complexity_metrics.txt"
# radon hal "$app_name" "$app_name|bugs|time|effort" >> $export_performance"complexity_metrics.txt"

# Tests and coverage reports
# coverage run --source=$app_name -m pytest tests
# coverage report -m > $export_performance-coverage_report.txt

Write-Output "Checking performance..."
# profile pyinstrument
# pyinstrument $export_performance"performance_pyinstrument.txt" -m "$app_name"\__init__.py
pyinstrument $app_name__init__.py > out #"performance_pyinstrument.txt" -m "$app_name"\__init__.py