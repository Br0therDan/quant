import {
  BacktestService,
  type BacktestCreate,
  type BacktestUpdate,
  type IntegratedBacktestRequest,
} from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutateAsyncFunction,
  type UseMutateFunction,
} from "@tanstack/react-query";
import { useMemo } from "react";

type UpdateBacktestVariables = {
  id: string;
  updateData: Partial<BacktestUpdate>;
};

type RunIntegratedBacktestVariables = IntegratedBacktestRequest;

type CreateBacktestFn = UseMutateFunction<
  Awaited<ReturnType<typeof BacktestService.createBacktest>>["data"],
  unknown,
  BacktestCreate,
  unknown
>;

type UpdateBacktestFn = UseMutateFunction<
  Awaited<ReturnType<typeof BacktestService.updateBacktest>>["data"],
  unknown,
  UpdateBacktestVariables,
  unknown
>;

type DeleteBacktestFn = UseMutateFunction<
  Awaited<ReturnType<typeof BacktestService.deleteBacktest>>["data"],
  unknown,
  string,
  unknown
>;

type RunIntegratedBacktestFn = UseMutateFunction<
  Awaited<ReturnType<typeof BacktestService.createAndRunIntegratedBacktest>>["data"],
  unknown,
  RunIntegratedBacktestVariables,
  unknown
>;

export const backtestQueryKeys = {
  all: ["backtest"] as const,
  lists: () => [...backtestQueryKeys.all, "list"] as const,
  list: (filters: string) => [...backtestQueryKeys.lists(), { filters }] as const,
  details: () => [...backtestQueryKeys.all, "detail"] as const,
  detail: (id: string) => [...backtestQueryKeys.details(), id] as const,
  results: () => [...backtestQueryKeys.all, "result"] as const,
  result: (id: string) => [...backtestQueryKeys.results(), id] as const,
  analytics: () => [...backtestQueryKeys.all, "analytics"] as const,
  performanceState: () => [...backtestQueryKeys.analytics(), "performanceState"] as const,
  tradeState: () => [...backtestQueryKeys.analytics(), "tradeState"] as const,
  summaryState: () => [...backtestQueryKeys.analytics(), "summaryState"] as const,
  healthState: () => [...backtestQueryKeys.all, "healthState"] as const,
} as const;

export function useBacktest() {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useSnackbar();

  const backtestListQuery = useQuery({
    queryKey: backtestQueryKeys.lists(),
    queryFn: async () => {
      const response = await BacktestService.getBacktests();
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  const backtestResultsQuery = useQuery({
    queryKey: backtestQueryKeys.results(),
    queryFn: async () => {
      const response = await BacktestService.getBacktestResults();
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  const backtestPerformanceAnalyticsQuery = useQuery({
    queryKey: backtestQueryKeys.performanceState(),
    queryFn: async () => {
      const response = await BacktestService.getPerformanceAnalytics();
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  const backtestTradeAnalyticsQuery = useQuery({
    queryKey: backtestQueryKeys.tradeState(),
    queryFn: async () => {
      const response = await BacktestService.getTradesAnalytics();
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  const backtestSummaryAnalyticsQuery = useQuery({
    queryKey: [...backtestQueryKeys.analytics(), "summary"],
    queryFn: async () => {
      const response = await BacktestService.getBacktestSummaryAnalytics();
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  const backtestHealthCheckQuery = useQuery({
    queryKey: backtestQueryKeys.healthState(),
    queryFn: async () => {
      const response = await BacktestService.healthCheck();
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  const createBacktestMutation = useMutation({
    mutationFn: async (data: BacktestCreate) => {
      const response = await BacktestService.createBacktest({ body: data });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
      showSuccess(
        `백테스트 "${data?.name || "새 백테스트"}"가 성공적으로 생성되었습니다`,
      );
    },
    onError: (error) => {
      console.error("백테스트 생성 실패:", error);
      showError(
        error instanceof Error
          ? error.message
          : "백테스트 생성에 실패했습니다",
      );
    },
  });

  const updateBacktestMutation = useMutation({
    mutationFn: async ({ id, updateData }: UpdateBacktestVariables) => {
      const response = await BacktestService.updateBacktest({
        path: { backtest_id: id },
        body: updateData,
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
      if (data?.id) {
        queryClient.invalidateQueries({ queryKey: backtestQueryKeys.detail(data.id) });
      }
      showSuccess(
        `백테스트 "${data?.name || "백테스트"}"가 성공적으로 업데이트되었습니다`,
      );
    },
    onError: (error) => {
      console.error("백테스트 업데이트 실패:", error);
      showError(
        error instanceof Error
          ? error.message
          : "백테스트 업데이트에 실패했습니다",
      );
    },
  });

  const deleteBacktestMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await BacktestService.deleteBacktest({
        path: { backtest_id: id },
      });
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
      queryClient.removeQueries({ queryKey: backtestQueryKeys.detail(id) });
      showSuccess("백테스트가 성공적으로 삭제되었습니다");
    },
    onError: (error) => {
      console.error("백테스트 삭제 실패:", error);
      showError(
        error instanceof Error
          ? error.message
          : "백테스트 삭제에 실패했습니다",
      );
    },
  });

  const runIntegratedBacktestMutation = useMutation({
    mutationFn: async (body: RunIntegratedBacktestVariables) => {
      const response = await BacktestService.createAndRunIntegratedBacktest({
        body,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
      showSuccess("통합 백테스트 실행이 시작되었습니다");
    },
    onError: (error) => {
      console.error("통합 백테스트 실행 실패:", error);
      showError(
        error instanceof Error
          ? error.message
          : "백테스트 실행에 실패했습니다",
      );
    },
  });

  return useMemo(
    () => ({
      backtestList: backtestListQuery.data,
      backtestResults: backtestResultsQuery.data,
      backtestPerformanceAnalytics: backtestPerformanceAnalyticsQuery.data,
      backtestTradeAnalytics: backtestTradeAnalyticsQuery.data,
      backtestSummaryAnalytics: backtestSummaryAnalyticsQuery.data,
      backtestHealthCheck: backtestHealthCheckQuery.data,
      isError: {
        backtestList: backtestListQuery.isError,
        backtestResults: backtestResultsQuery.isError,
        backtestPerformanceAnalytics: backtestPerformanceAnalyticsQuery.isError,
        backtestTradeAnalytics: backtestTradeAnalyticsQuery.isError,
        backtestSummaryAnalytics: backtestSummaryAnalyticsQuery.isError,
        backtestHealthCheck: backtestHealthCheckQuery.isError,
      },
      isLoading: {
        backtestList: backtestListQuery.isLoading,
        backtestResults: backtestResultsQuery.isLoading,
        backtestPerformanceAnalytics: backtestPerformanceAnalyticsQuery.isLoading,
        backtestTradeAnalytics: backtestTradeAnalyticsQuery.isLoading,
        backtestSummaryAnalytics: backtestSummaryAnalyticsQuery.isLoading,
        backtestHealthCheck: backtestHealthCheckQuery.isLoading,
      },
      isMutating: {
        createBacktest: createBacktestMutation.isPending,
        updateBacktest: updateBacktestMutation.isPending,
        deleteBacktest: deleteBacktestMutation.isPending,
        runIntegratedBacktest: runIntegratedBacktestMutation.isPending,
      },
      createBacktest: createBacktestMutation.mutate as CreateBacktestFn,
      createBacktestAsync:
        createBacktestMutation.mutateAsync as UseMutateAsyncFunction<
          Awaited<ReturnType<typeof BacktestService.createBacktest>>["data"],
          unknown,
          BacktestCreate,
          unknown
        >,
      updateBacktest: updateBacktestMutation.mutate as UpdateBacktestFn,
      updateBacktestAsync:
        updateBacktestMutation.mutateAsync as UseMutateAsyncFunction<
          Awaited<ReturnType<typeof BacktestService.updateBacktest>>["data"],
          unknown,
          UpdateBacktestVariables,
          unknown
        >,
      deleteBacktest: deleteBacktestMutation.mutate as DeleteBacktestFn,
      deleteBacktestAsync:
        deleteBacktestMutation.mutateAsync as UseMutateAsyncFunction<
          Awaited<ReturnType<typeof BacktestService.deleteBacktest>>["data"],
          unknown,
          string,
          unknown
        >,
      runIntegratedBacktest: runIntegratedBacktestMutation.mutate as RunIntegratedBacktestFn,
      runIntegratedBacktestAsync:
        runIntegratedBacktestMutation.mutateAsync as UseMutateAsyncFunction<
          Awaited<
            ReturnType<typeof BacktestService.createAndRunIntegratedBacktest>
          >["data"],
          unknown,
          RunIntegratedBacktestVariables,
          unknown
        >,
      refetch: {
        list: backtestListQuery.refetch,
        results: backtestResultsQuery.refetch,
        performance: backtestPerformanceAnalyticsQuery.refetch,
        trades: backtestTradeAnalyticsQuery.refetch,
        summary: backtestSummaryAnalyticsQuery.refetch,
        health: backtestHealthCheckQuery.refetch,
      },
    }),
    [
      backtestHealthCheckQuery,
      backtestListQuery,
      backtestPerformanceAnalyticsQuery,
      backtestResultsQuery,
      backtestSummaryAnalyticsQuery,
      backtestTradeAnalyticsQuery,
      createBacktestMutation,
      deleteBacktestMutation,
      runIntegratedBacktestMutation,
      updateBacktestMutation,
    ],
  );
}

export const useBacktestDetail = (id: string) =>
  useQuery({
    queryKey: backtestQueryKeys.detail(id),
    queryFn: async () => {
      const response = await BacktestService.getBacktest({
        path: { backtest_id: id },
      });
      return response.data;
    },
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });
