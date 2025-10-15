/**
 * Evaluation Harness Management Hook
 *
 * Manages model evaluation scenarios and runs for MLOps platform.
 * Provides comprehensive model assessment and comparison capabilities.
 *
 * @module hooks/useEvaluationHarness
 */

import type {
	AbTestCreate,
	AbTestResponse,
	BenchmarkCreate,
	BenchmarkResponse,
	BenchmarkRunRequest,
	BenchmarkRunResponse,
	DetailedMetrics,
	EvaluationRequest,
	EvaluationRunResponse,
	EvaluationStatus,
	FairnessAuditRequest,
	FairnessReportResponse,
	ScenarioCreate,
	ScenarioResponse,
	ScenarioUpdate,
	TestCaseCreate,
} from "@/client";
import { EvaluationHarnessService, MlService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ============================================================================
// Types (using backend-generated types)
// ============================================================================

export type Scenario = ScenarioResponse;
export type EvaluationRun = EvaluationRunResponse;

// Create/Update DTOs
export type ScenarioCreateDTO = ScenarioCreate;
export type ScenarioUpdateDTO = ScenarioUpdate;

// Benchmark types
export type Benchmark = BenchmarkResponse;
export type BenchmarkRun = BenchmarkRunResponse;
export type { BenchmarkCreate, BenchmarkRunRequest, TestCaseCreate };

// A/B Testing types
export type ABTest = AbTestResponse;
export type { AbTestCreate as ABTestCreate };

// Fairness types
export type FairnessReport = FairnessReportResponse;
export type { FairnessAuditRequest };

// Re-export enums for convenience
export type { EvaluationStatus };

// ============================================================================
// Query Keys
// ============================================================================

export const evaluationHarnessQueryKeys = {
	all: ["evaluationHarness"] as const,
	scenarios: () => [...evaluationHarnessQueryKeys.all, "scenarios"] as const,
	scenarioDetail: (name: string) =>
		[...evaluationHarnessQueryKeys.scenarios(), "detail", name] as const,
	runs: () => [...evaluationHarnessQueryKeys.all, "runs"] as const,
	runDetail: (runId: string) =>
		[...evaluationHarnessQueryKeys.runs(), "detail", runId] as const,
	benchmarks: () => [...evaluationHarnessQueryKeys.all, "benchmarks"] as const,
	benchmarkDetail: (name: string) =>
		[...evaluationHarnessQueryKeys.benchmarks(), "detail", name] as const,
	abTests: () => [...evaluationHarnessQueryKeys.all, "abTests"] as const,
	abTestDetail: (id: string) =>
		[...evaluationHarnessQueryKeys.abTests(), "detail", id] as const,
	fairness: () => [...evaluationHarnessQueryKeys.all, "fairness"] as const,
	fairnessDetail: (id: string) =>
		[...evaluationHarnessQueryKeys.fairness(), "detail", id] as const,
};

// ============================================================================
// Hook Implementation
// ============================================================================

export const useEvaluationHarness = () => {
	const queryClient = useQueryClient();
	const { showSuccess, showError } = useSnackbar();

	// ============================================================================
	// Queries
	// ============================================================================

	/**
	 * Query: Scenarios List
	 * Fetches list of all evaluation scenarios
	 */
	const scenariosQuery = useQuery({
		queryKey: evaluationHarnessQueryKeys.scenarios(),
		queryFn: async (): Promise<Scenario[]> => {
			const response = await EvaluationHarnessService.listScenarios();
			return response.data ?? [];
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
	});

	/**
	 * Query: Evaluation Runs List
	 * Fetches list of evaluation runs
	 */
	const runsQuery = useQuery({
		queryKey: evaluationHarnessQueryKeys.runs(),
		queryFn: async (): Promise<EvaluationRun[]> => {
			const response = await EvaluationHarnessService.listEvaluationRuns();
			return response.data ?? [];
		},
		staleTime: 1000 * 60 * 2, // 2 minutes
	});

	/**
	 * Query: Benchmarks List
	 * Fetches list of all benchmarks
	 */
	const benchmarksQuery = useQuery({
		queryKey: evaluationHarnessQueryKeys.benchmarks(),
		queryFn: async (): Promise<Benchmark[]> => {
			const response = await MlService.listBenchmarks();
			return response.data ?? [];
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
	});

	/**
	 * Query: A/B Tests List
	 * Fetches list of all A/B tests
	 */
	const abTestsQuery = useQuery({
		queryKey: evaluationHarnessQueryKeys.abTests(),
		queryFn: async (): Promise<ABTest[]> => {
			const response = await MlService.listAbTests();
			return response.data ?? [];
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
	});

	/**
	 * Query: Fairness Reports List
	 * Fetches list of all fairness audit reports
	 */
	const fairnessQuery = useQuery({
		queryKey: evaluationHarnessQueryKeys.fairness(),
		queryFn: async (): Promise<FairnessReport[]> => {
			const response = await MlService.listFairnessReports();
			return response.data ?? [];
		},
		staleTime: 1000 * 60 * 5, // 5 minutes
	});

	// ============================================================================
	// Mutations
	// ============================================================================

	/**
	 * Mutation: Create Scenario
	 * Creates a new evaluation scenario
	 */
	const createScenarioMutation = useMutation({
		mutationFn: async (data: ScenarioCreate): Promise<Scenario> => {
			const response = await EvaluationHarnessService.registerScenario({
				body: data,
			});
			if (!response.data) {
				throw new Error("Scenario creation failed");
			}
			return response.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: evaluationHarnessQueryKeys.scenarios(),
			});
			showSuccess("시나리오가 성공적으로 생성되었습니다");
		},
		onError: (error: Error) => {
			showError(`시나리오 생성 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Update Scenario
	 * Updates an existing scenario
	 */
	const updateScenarioMutation = useMutation({
		mutationFn: async ({
			name,
			data,
		}: {
			name: string;
			data: ScenarioUpdate;
		}): Promise<Scenario> => {
			const response = await EvaluationHarnessService.updateScenario({
				path: { name },
				body: data,
			});
			if (!response.data) {
				throw new Error("Scenario update failed");
			}
			return response.data;
		},
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: evaluationHarnessQueryKeys.scenarios(),
			});
			queryClient.invalidateQueries({
				queryKey: evaluationHarnessQueryKeys.scenarioDetail(variables.name),
			});
			showSuccess("시나리오가 성공적으로 업데이트되었습니다");
		},
		onError: (error: Error) => {
			showError(`시나리오 업데이트 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Run Evaluation
	 * Starts a new evaluation run
	 */
	const runEvaluationMutation = useMutation({
		mutationFn: async (data: EvaluationRequest): Promise<EvaluationRun> => {
			const response = await EvaluationHarnessService.runEvaluation({
				body: data,
			});
			if (!response.data) {
				throw new Error("Evaluation run failed");
			}
			return response.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: evaluationHarnessQueryKeys.runs(),
			});
			showSuccess("평가가 성공적으로 시작되었습니다");
		},
		onError: (error: Error) => {
			showError(`평가 실행 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Create Benchmark
	 * Creates a new benchmark suite
	 */
	const createBenchmarkMutation = useMutation({
		mutationFn: async (data: BenchmarkCreate): Promise<Benchmark> => {
			const response = await MlService.createBenchmark({ body: data });
			if (!response.data) {
				throw new Error("Failed to create benchmark");
			}
			return response.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: evaluationHarnessQueryKeys.benchmarks(),
			});
			showSuccess("벤치마크가 생성되었습니다");
		},
		onError: (error: Error) => {
			showError(`벤치마크 생성 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Run Benchmark
	 * Executes a benchmark suite
	 */
	const runBenchmarkMutation = useMutation({
		mutationFn: async (data: BenchmarkRunRequest): Promise<BenchmarkRun> => {
			const response = await MlService.runBenchmark({ body: data });
			if (!response.data) {
				throw new Error("Failed to run benchmark");
			}
			return response.data;
		},
		onSuccess: () => {
			showSuccess("벤치마크가 실행되었습니다");
		},
		onError: (error: Error) => {
			showError(`벤치마크 실행 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Create A/B Test
	 * Creates a new A/B test
	 */
	const createABTestMutation = useMutation({
		mutationFn: async (data: AbTestCreate): Promise<ABTest> => {
			const response = await MlService.createAbTest({ body: data });
			if (!response.data) {
				throw new Error("Failed to create A/B test");
			}
			return response.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: evaluationHarnessQueryKeys.abTests(),
			});
			showSuccess("A/B 테스트가 생성되었습니다");
		},
		onError: (error: Error) => {
			showError(`A/B 테스트 생성 실패: ${error.message}`);
		},
	});

	/**
	 * Mutation: Request Fairness Audit
	 * Requests a fairness audit for a model
	 */
	const requestFairnessAuditMutation = useMutation({
		mutationFn: async (data: FairnessAuditRequest): Promise<FairnessReport> => {
			const response = await MlService.requestFairnessAudit({ body: data });
			if (!response.data) {
				throw new Error("Failed to request fairness audit");
			}
			return response.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: evaluationHarnessQueryKeys.fairness(),
			});
			showSuccess("공정성 감사가 요청되었습니다");
		},
		onError: (error: Error) => {
			showError(`공정성 감사 요청 실패: ${error.message}`);
		},
	});

	// ============================================================================
	// Return Hook Interface
	// ============================================================================

	return {
		// Queries
		scenariosList: scenariosQuery.data || [],
		isLoadingScenarios: scenariosQuery.isLoading,
		scenariosError: scenariosQuery.error,

		runsList: runsQuery.data || [],
		isLoadingRuns: runsQuery.isLoading,
		runsError: runsQuery.error,

		// Mutations
		createScenario: createScenarioMutation.mutateAsync,
		isCreatingScenario: createScenarioMutation.isPending,

		updateScenario: (name: string, data: ScenarioUpdate) =>
			updateScenarioMutation.mutateAsync({ name, data }),
		isUpdatingScenario: updateScenarioMutation.isPending,

		runEvaluation: runEvaluationMutation.mutateAsync,
		isRunningEvaluation: runEvaluationMutation.isPending,

		// Refetch functions
		refetchScenarios: scenariosQuery.refetch,
		refetchRuns: runsQuery.refetch,

		// Benchmark
		benchmarksList: benchmarksQuery.data || [],
		isLoadingBenchmarks: benchmarksQuery.isLoading,
		benchmarksError: benchmarksQuery.error,
		createBenchmark: createBenchmarkMutation.mutateAsync,
		isCreatingBenchmark: createBenchmarkMutation.isPending,
		runBenchmark: runBenchmarkMutation.mutateAsync,
		isRunningBenchmark: runBenchmarkMutation.isPending,
		refetchBenchmarks: benchmarksQuery.refetch,

		// A/B Testing
		abTestsList: abTestsQuery.data || [],
		isLoadingABTests: abTestsQuery.isLoading,
		abTestsError: abTestsQuery.error,
		createABTest: createABTestMutation.mutateAsync,
		isCreatingABTest: createABTestMutation.isPending,
		refetchABTests: abTestsQuery.refetch,

		// Fairness
		fairnessList: fairnessQuery.data || [],
		isLoadingFairness: fairnessQuery.isLoading,
		fairnessError: fairnessQuery.error,
		requestFairnessAudit: requestFairnessAuditMutation.mutateAsync,
		isRequestingAudit: requestFairnessAuditMutation.isPending,
		refetchFairness: fairnessQuery.refetch,
	};
};

// ============================================================================
// Additional Hooks for Detail Views
// ============================================================================

/**
 * Hook: Evaluation Run Detail
 * Fetches detailed report for a specific evaluation run
 */
export const useEvaluationRunDetail = (runId: string | null) => {
	const runDetailQuery = useQuery({
		queryKey: evaluationHarnessQueryKeys.runDetail(runId || ""),
		queryFn: async () => {
			if (!runId) {
				throw new Error("Run ID is required");
			}
			const response = await EvaluationHarnessService.getEvaluationReport({
				path: { run_id: runId },
			});
			return response.data;
		},
		enabled: !!runId,
		staleTime: 1000 * 60 * 5,
	});

	return {
		runDetail: runDetailQuery.data,
		isLoading: runDetailQuery.isLoading,
		error: runDetailQuery.error,
		refetch: runDetailQuery.refetch,
	};
};

/**
 * Hook: Detailed Evaluation Metrics
 * Fetches detailed metrics for a specific evaluation run (confusion matrix, ROC curve, etc.)
 */
export const useDetailedMetrics = (runId: string | null) => {
	const detailedMetricsQuery = useQuery({
		queryKey: [...evaluationHarnessQueryKeys.runDetail(runId || ""), "metrics"],
		queryFn: async (): Promise<DetailedMetrics> => {
			if (!runId) {
				throw new Error("Run ID is required");
			}
			const response = await MlService.getDetailedMetrics({
				path: { run_id: runId },
			});
			if (!response.data) {
				throw new Error("Detailed metrics not found");
			}
			return response.data;
		},
		enabled: !!runId,
		staleTime: 1000 * 60 * 10, // 10분 (메트릭은 변경되지 않음)
	});

	return {
		detailedMetrics: detailedMetricsQuery.data,
		isLoading: detailedMetricsQuery.isLoading,
		error: detailedMetricsQuery.error,
		refetch: detailedMetricsQuery.refetch,
	};
};

// ============================================================================
// Benchmark Hooks
// ============================================================================

export const useBenchmarkDetail = (benchmarkName: string | null) => {
	const benchmarkDetailQuery = useQuery({
		queryKey: evaluationHarnessQueryKeys.benchmarkDetail(benchmarkName || ""),
		queryFn: async () => {
			if (!benchmarkName) {
				throw new Error("Benchmark name is required");
			}
			// Note: Backend doesn't have GET /benchmarks/{name} endpoint yet
			// For now, we fetch the list and filter
			const response = await MlService.listBenchmarks();
			const benchmark = response.data?.find((b) => b.name === benchmarkName);
			if (!benchmark) {
				throw new Error(`Benchmark '${benchmarkName}' not found`);
			}
			return benchmark;
		},
		enabled: !!benchmarkName,
		staleTime: 1000 * 60 * 5,
	});

	return {
		benchmarkDetail: benchmarkDetailQuery.data,
		isLoading: benchmarkDetailQuery.isLoading,
		error: benchmarkDetailQuery.error,
		refetch: benchmarkDetailQuery.refetch,
	};
};

export const useBenchmarkRun = (runId: string | null) => {
	const benchmarkRunQuery = useQuery({
		queryKey: [...evaluationHarnessQueryKeys.benchmarks(), "run", runId || ""],
		queryFn: async () => {
			if (!runId) {
				throw new Error("Run ID is required");
			}
			// Note: Backend doesn't have GET /benchmarks/runs/{id} endpoint yet
			// This is a placeholder - backend needs to add this endpoint
			throw new Error("Benchmark run detail endpoint not implemented");
		},
		enabled: !!runId,
		staleTime: 1000 * 60 * 5,
	});

	return {
		benchmarkRun: benchmarkRunQuery.data,
		isLoading: benchmarkRunQuery.isLoading,
		error: benchmarkRunQuery.error,
		refetch: benchmarkRunQuery.refetch,
	};
};

// ============================================================================
// A/B Testing Hooks
// ============================================================================

export const useABTestDetail = (testId: string | null) => {
	const abTestDetailQuery = useQuery({
		queryKey: evaluationHarnessQueryKeys.abTestDetail(testId || ""),
		queryFn: async () => {
			if (!testId) {
				throw new Error("Test ID is required");
			}
			const response = await MlService.getAbTest({ path: { test_id: testId } });
			if (!response.data) {
				throw new Error(`A/B Test '${testId}' not found`);
			}
			return response.data;
		},
		enabled: !!testId,
		staleTime: 1000 * 60 * 5,
	});

	return {
		abTestDetail: abTestDetailQuery.data,
		isLoading: abTestDetailQuery.isLoading,
		error: abTestDetailQuery.error,
		refetch: abTestDetailQuery.refetch,
	};
};

// ============================================================================
// Fairness Audit Hooks
// ============================================================================

export const useFairnessReport = (reportId: string | null) => {
	const fairnessReportQuery = useQuery({
		queryKey: evaluationHarnessQueryKeys.fairnessDetail(reportId || ""),
		queryFn: async () => {
			if (!reportId) {
				throw new Error("Report ID is required");
			}
			const response = await MlService.getFairnessReport({
				path: { report_id: reportId },
			});
			if (!response.data) {
				throw new Error(`Fairness report '${reportId}' not found`);
			}
			return response.data;
		},
		enabled: !!reportId,
		staleTime: 1000 * 60 * 5,
	});

	return {
		fairnessReport: fairnessReportQuery.data,
		isLoading: fairnessReportQuery.isLoading,
		error: fairnessReportQuery.error,
		refetch: fairnessReportQuery.refetch,
	};
};
